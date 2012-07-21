<%!
    from datetime import datetime
    from hashlib import sha256
    from itertools import count
    from os.path import expanduser
    from re import sub, UNICODE
    from sys import path
    from time import time
    from urlparse import parse_qs, urlparse

    from earwigbot import exceptions
    from earwigbot.bot import Bot
    import oursql

    def get_results(bot, lang, project, name, all_projects, title, url, query):
        site = get_site(bot, lang, project, name, all_projects)
        if not site:
            return None, None, None
        page = site.get_page(title)
        try:
            page.get()  # Make sure that the page exists before we check it!
        except (exceptions.PageNotFoundError, exceptions.InvalidPageError):
            return site, page, None

        # if url:
        #     result = get_url_specific_results(page, url)
        # else:
        #     conn = open_sql_connection(bot, "copyvioCache")
        #     if not query.get("nocache"):
        #         result = get_cached_results(page, conn)
        #     if query.get("nocache") or not result:
        #         result = get_fresh_results(page, conn)
        tstart = time()
        mc1 = __import__("earwigbot").wiki.copyvios.MarkovChain(page.get())
        mc2 = __import__("earwigbot").wiki.copyvios.MarkovChain(u"This is some random textual content for a page.")
        mci = __import__("earwigbot").wiki.copyvios.MarkovChainIntersection(mc1, mc2)
        result = __import__("earwigbot").wiki.copyvios.CopyvioCheckResult(
            True, 0.67123, "http://example.com/", 7, mc1, (mc2, mci))
        result.cached = False
        result.tdiff = time() - tstart
        # END TEST BLOCK
        return site, page, result

    def get_site(bot, lang, project, name, all_projects):
        if project not in [proj[0] for proj in all_projects]:
            return None
        if project == "wikimedia" and name:  # Special sites:
            try:
                return bot.wiki.get_site(name=name)
            except exceptions.SiteNotFoundError:
                try:
                    return bot.wiki.add_site(lang=lang, project=project)
                except (exceptions.APIError, exceptions.LoginError):
                    return None
        try:
            return bot.wiki.get_site(lang=lang, project=project)
        except exceptions.SiteNotFoundError:
            try:
                return bot.wiki.add_site(lang=lang, project=project)
            except (exceptions.APIError, exceptions.LoginError):
                return None

    def get_url_specific_results(page, url):
        t_start = time()
        result = page.copyvio_compare(url)
        result.cached = False
        result.tdiff = time() - t_start
        return result

    def open_sql_connection(bot, dbname):
        conn_args = bot.config.wiki["_toolserverSQL"][dbname]
        if "read_default_file" not in conn_args and "user" not in conn_args and "passwd" not in conn_args:
            conn_args["read_default_file"] = expanduser("~/.my.cnf")
        if "autoping" not in conn_args:
            conn_args["autoping"] = True
        if "autoreconnect" not in conn_args:
            conn_args["autoreconnect"] = True
        return oursql.connect(**conn_args)

    def get_cached_results(page, conn):
        query1 = "DELETE FROM cache WHERE cache_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)"
        query2 = "SELECT cache_url, cache_time, cache_queries, cache_process_time FROM cache WHERE cache_id = ? AND cache_hash = ?"
        pageid = page.pageid()
        hash = sha256(page.get()).hexdigest()
        t_start = time()

        with conn.cursor() as cursor:
            cursor.execute(query1)
            cursor.execute(query2, (pageid, hash))
            results = cursor.fetchall()
            if not results:
                return None

        url, cache_time, num_queries, original_tdiff = results[0]
        result = page.copyvio_compare(url)
        result.cached = True
        result.queries = num_queries
        result.tdiff = time() - t_start
        result.original_tdiff = original_tdiff
        result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
        result.cache_age = format_date(cache_time)
        return result

    def format_date(cache_time):
        diff = datetime.utcnow() - cache_time
        if diff.seconds > 3600:
            return "{0} hours".format(diff.seconds / 3600)
        if diff.seconds > 60:
            return "{0} minutes".format(diff.seconds / 60)
        return "{0} seconds".format(diff.seconds)

    def get_fresh_results(page, conn):
        t_start = time()
        result = page.copyvio_check(max_queries=10)
        result.cached = False
        result.tdiff = time() - t_start
        cache_result(page, result, conn)
        return result

    def cache_result(page, result, conn):
        pageid = page.pageid()
        hash = sha256(page.get()).hexdigest()
        query1 = "SELECT 1 FROM cache WHERE cache_id = ?"
        query2 = "DELETE FROM cache WHERE cache_id = ?"
        query3 = "INSERT INTO cache VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)"
        with conn.cursor() as cursor:
            cursor.execute(query1, (pageid,))
            if cursor.fetchall():
                cursor.execute(query2, (pageid,))
            cursor.execute(query3, (pageid, hash, result.url, result.queries,
                                    result.tdiff))

    def get_sites(bot):
        max_staleness = 60 * 60 * 24 * 7
        conn = open_sql_connection(bot, "globals")
        query1 = "SELECT update_time FROM updates WHERE update_service = ?"
        query2 = "SELECT lang_code, lang_name FROM language"
        query3 = "SELECT project_code, project_name FROM project"
        with conn.cursor() as cursor:
            cursor.execute(query1, ("sites",))
            try:
                time_since_update = int(time() - cursor.fetchall()[0][0])
            except IndexError:
                time_since_update = time()
            if time_since_update > max_staleness:
                update_sites(bot.wiki.get_site(), cursor)
            cursor.execute(query2)
            langs = []
            for code, name in cursor.fetchall():
                if "\U" in name:
                    name = name.decode("unicode_escape")
                langs.append((code, name))
            cursor.execute(query3)
            projects = cursor.fetchall()
        return langs, projects

    def update_sites(site, cursor):
        matrix = site.api_query(action="sitematrix")["sitematrix"]
        del matrix["count"]
        languages, projects = set(), set()
        for site in matrix.itervalues():
            if isinstance(site, list):  # Special sites
                bad_sites = ["closed", "private", "fishbowl"]
                for special in site:
                    if all([key not in special for key in bad_sites]):
                        full = urlparse(special["url"]).netloc
                        if full.count(".") == 1:  # No subdomain, so use "www"
                            lang, project = "www", full.split(".")[0]
                        else:
                            lang, project = full.rsplit(".", 2)[:2]
                        code = u"{0}::{1}".format(lang, special["dbname"])
                        name = special["code"].capitalize()
                        languages.add((code, u"{0} ({1})".format(lang, name)))
                        projects.add((project, project.capitalize()))
                continue
            this = set()
            for web in site["site"]:
                if "closed" in web:
                    continue
                project = "wikipedia" if web["code"] == u"wiki" else web["code"]
                this.add((project, project.capitalize()))
            if this:
                code = site["code"]
                if "\U" in site["name"].encode("unicode_escape"):
                    name = site["name"].encode("unicode_escape")
                else:
                    name = site["name"]
                languages.add((code, u"{0} ({1})".format(code, name)))
                projects |= this
        save_site_updates(cursor, languages, projects)

    def save_site_updates(cursor, languages, projects):
        query1 = "SELECT lang_code, lang_name FROM language"
        query2 = "DELETE FROM language WHERE lang_code = ? AND lang_name = ?"
        query3 = "INSERT INTO language VALUES (?, ?)"
        query4 = "SELECT project_code, project_name FROM project"
        query5 = "DELETE FROM project WHERE project_code = ? AND project_name = ?"
        query6 = "INSERT INTO project VALUES (?, ?)"
        query7 = "SELECT 1 FROM updates WHERE update_service = ?"
        query8 = "UPDATE updates SET update_time = ? WHERE update_service = ?"
        query9 = "INSERT INTO updates VALUES (?, ?)"
        synchronize_sites_with_db(cursor, languages, query1, query2, query3)
        synchronize_sites_with_db(cursor, projects, query4, query5, query6)
        cursor.execute(query7, ("sites",))
        if cursor.fetchall():
            cursor.execute(query8, (time(), "sites"))
        else:
            cursor.execute(query9, ("sites", time()))

    def synchronize_sites_with_db(cursor, updates, q_list, q_rmv, q_update):
        removals = []
        cursor.execute(q_list)
        for site in cursor:
            updates.remove(site) if site in updates else removals.append(site)
        cursor.executemany(q_rmv, removals)
        cursor.executemany(q_update, updates)

    def highlight_delta(chain, delta):
        processed = []
        prev_prev = prev = chain.START
        i = 0
        all_words = chain.text.split()
        paragraphs = chain.text.split("\n")
        for paragraph in paragraphs:
            processed_words = []
            words = paragraph.split(" ")
            for word, i in zip(words, count(i)):
                try:
                    next = strip_word(all_words[i+1])
                except IndexError:
                    next = chain.END
                sword = strip_word(word)
                block = (prev_prev, prev)  # Block for before
                alock = (prev, sword)  # Block for after
                before = [block in delta.chain and sword in delta.chain[block]]
                after = [alock in delta.chain and next in delta.chain[alock]]
                is_first = i == 0
                is_last = i + 1 == len(all_words)
                res = highlight_word(word, before, after, is_first, is_last)
                processed_words.append(res)
                prev_prev = prev
                prev = sword
            processed.append(u" ".join(processed_words))
            i += 1
        return u"<br /><br />".join(processed)

    def highlight_word(word, before, after, is_first, is_last):
        if before and after:
            # Word is in the middle of a highlighted block, so don't change
            # anything unless this is the first word (force block to start) or
            # the last word (force block to end):
            res = word
            if is_first:
                res = u'<span class="cv-hl">' + res
            if is_last:
                res += u'</span>'
        elif before:
            # Word is the last in a highlighted block, so fade it out and then
            # end the block; force open a block before the word if this is the
            # first word:
            res = fade_word(word, u"out") + u"</span>"
            if is_first:
                res = u'<span class="cv-hl">' + res
        elif after:
            # Word is the first in a highlighted block, so start the block and
            # then fade it in; force close the block after the word if this is
            # the last word:
            res = u'<span class="cv-hl">' + fade_word(word, u"in")
            if is_last:
                res += u"</span>"
        else:
            # Word is completely outside of a highlighted block, so do nothing:
            res = word
        return res

    def fade_word(word, dir):
        if len(word) <= 4:
            return u'<span class="cv-hl-{0}">{1}</span>'.format(dir, word)
        if dir == u"out":
            return u'{0}<span class="cv-hl-out">{1}</span>'.format(word[:-4], word[-4:])
        return u'<span class="cv-hl-in">{0}</span>{1}'.format(word[:4], word[4:])

    def strip_word(word):
        return sub("[^\w\s-]", "", word.lower(), flags=UNICODE)

    def urlstrip(url):
        if url.startswith("http://"):
            url = url[7:]
        if url.startswith("https://"):
            url = url[8:]
        if url.startswith("www."):
            url = url[4:]
        if url.endswith("/"):
            url = url[:-1]
        return url
%>\
<%
    lang = orig_lang = project = name = title = url = None
    query = parse_qs(environ["QUERY_STRING"])
    if "lang" in query:
        lang = orig_lang = query["lang"][0].decode("utf8").lower()
        if "::" in lang:
            lang, name = lang.split("::", 1)
    if "project" in query:
        project = query["project"][0].decode("utf8").lower()
    if "title" in query:
        title = query["title"][0].decode("utf8")
    if "url" in query:
        url = query["url"][0].decode("utf8")
    bot = Bot(".earwigbot")
    all_langs, all_projects = get_sites(bot)
    if lang and project and title:
        site, page, result = get_results(bot, lang, project, name,
                                         all_projects, title, url, query)
    else:
        site = page = result = None
%>\
<%include file="/support/header.mako" args="environ=environ, title='Copyvio Detector', add_css=('copyvios.css',), add_js=('copyvios.js',)"/>
            <h1>Copyvio Detector</h1>
            <p>This tool attempts to detect <a href="//en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in articles. Simply give the title of the page you want to check and hit Submit. The tool will then search for its content elsewhere on the web and display a report if a similar webpage is found. If you also provide a URL, it will not query any search engines and instead display a report comparing the article to that particular webpage, like the <a href="//toolserver.org/~dcoetzee/duplicationdetector/">Duplication Detector</a>. Check out the <a href="//en.wikipedia.org/wiki/User:EarwigBot/Copyvios/FAQ">FAQ</a> for more information and technical details.</p>
            <form action="${environ['PATH_INFO']}" method="get">
                <table>
                    <tr>
                        <td>Site:</td>
                        <td>
                            <tt>http://</tt>
                            <select name="lang">
                                <% selected_lang = orig_lang if orig_lang else bot.wiki.get_site().lang %>
                                % for code, name in all_langs:
                                    % if code == selected_lang:
                                        <option value="${code}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                            <tt>.</tt>
                            <select name="project">
                                <% selected_project = project if project else bot.wiki.get_site().project %>
                                % for code, name in all_projects:
                                    % if code == selected_project:
                                        <option value="${code}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                            <tt>.org</tt>
                        </td>
                    </tr>
                    <tr>
                        <td>Page title:</td>
                        % if page:
                            <td><input type="text" name="title" size="60" value="${page.title | h}" /></td>
                        % elif title:
                            <td><input type="text" name="title" size="60" value="${title | h}" /></td>
                        % else:
                            <td><input type="text" name="title" size="60" /></td>
                        % endif
                    </tr>
                    <tr>
                        <td>URL (optional):</td>
                        % if url:
                            <td><input type="text" name="url" size="120" value="${url | h}" /></td>
                        % else:
                            <td><input type="text" name="url" size="120" /></td>
                        % endif
                    </tr>
                    % if query.get("nocache") or (result and result.cached):
                        <tr>
                            <td>Bypass cache:</td>
                            % if query.get("nocache"):
                                <td><input type="checkbox" name="nocache" value="1" checked="checked" /></td>
                            % else:
                                <td><input type="checkbox" name="nocache" value="1" /></td>
                            % endif
                        </tr>
                    % endif
                    <tr>
                        <td><button type="submit">Submit</button></td>
                    </tr>
                </table>
            </form>
            % if project and lang and title and not page:
                <div class="divider"></div>
                <div id="cv-result-yes">
                    <p>The given site (project=<b><tt>${project}</tt></b>, language=<b><tt>${lang}</tt></b>) doesn't seem to exist. It may also be closed or private. <a href="//${lang}.${project}.org/">Confirm its URL.</a></p>
                </div>
            % elif project and lang and title and page and not result:
                <div class="divider"></div>
                <div id="cv-result-yes">
                    <p>The given page doesn't seem to exist: <a href="${page.url}">${page.title | h}</a>.</p>
                </div>
            % elif page:
                <div class="divider"></div>
                <div id="cv-result-${'yes' if result.violation else 'no'}">
                    % if result.violation:
                        <h2 id="cv-result-header"><a href="${page.url}">${page.title | h}</a> is a suspected violation of <a href="${result.url | h}">${result.url | urlstrip}</a>.</h2>
                    % else:
                        <h2 id="cv-result-header">No violations detected in <a href="${page.url()}">${page.title | h}</a>.</h2>
                    % endif
                    <ul id="cv-result-list">
                        <li><b><tt>${round(result.confidence * 100, 1)}%</tt></b> confidence of a violation.</li>
                        % if result.cached:
                            <li>Results are <a id="cv-cached" href="#">cached
                                <span>To save time (and money), this tool will retain the results of checks for up to 72 hours. This includes the URL of the "violated" source, but neither its content nor the content of the article. Future checks on the same page (assuming it remains unchanged) will not involve additional search queries, but a fresh comparison against the source URL will be made. If the page is modified, a new check will be run.</span>
                            </a> from ${result.cache_time} (${result.cache_age} ago). <a href="${environ['REQUEST_URI'].decode("utf8") | h}&amp;nocache=1">Bypass the cache.</a></li>
                        % else:
                            <li>Results generated in <tt>${round(result.tdiff, 3)}</tt> seconds using <tt>${result.queries}</tt> queries.</li>
                        % endif
                        <li><a id="cv-result-detail-link" href="#cv-result-detail" onclick="copyvio_toggle_details()">Show details:</a></li>
                    </ul>
                    <div id="cv-result-detail" style="display: none;">
                        <ul id="cv-result-detail-list">
                            <li>Trigrams: <i>Article:</i> <tt>${result.article_chain.size()}</tt> / <i>Source:</i> <tt>${result.source_chain.size()}</tt> / <i>Delta:</i> <tt>${result.delta_chain.size()}</tt></li>
                            % if result.cached:
                                % if result.queries:
                                    <li>Retrieved from cache in <tt>${round(result.tdiff, 3)}</tt> seconds (originally generated in <tt>${round(result.original_tdiff, 3)}</tt>s using <tt>${result.queries}</tt> queries; <tt>${round(result.original_tdiff - result.tdiff, 3)}</tt>s saved).</li>
                                % else:
                                    <li>Retrieved from cache in <tt>${round(result.tdiff, 3)}</tt> seconds (originally generated in <tt>${round(result.original_tdiff, 3)}</tt>s; <tt>${round(result.original_tdiff - result.tdiff, 3)}</tt>s saved).</li>
                                % endif
                            % endif
                            % if result.queries:
                                <li><i>Fun fact:</i> The Wikimedia Foundation paid Yahoo! Inc. <a href="http://info.yahoo.com/legal/us/yahoo/search/bosspricing/details.html">$${result.queries * 0.0008} USD</a> for these results.</li>
                            % endif
                        </ul>
                        <table id="cv-chain-table">
                            <tr>
                                <td>Article: <div class="cv-chain-detail"><p>${highlight_delta(result.article_chain, result.delta_chain)}</p></div></td>
                                <td>Source: <div class="cv-chain-detail"><p>${highlight_delta(result.source_chain, result.delta_chain)}</p></div></td>
                            </tr>
                        </table>
                    </div>
                </div>
            % endif
<%include file="/support/footer.mako" args="environ=environ"/>
