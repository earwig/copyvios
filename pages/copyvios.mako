<%!
    from collections import defaultdict
    from datetime import datetime
    from hashlib import sha256
    from itertools import count
    from os.path import expanduser
    from re import sub, UNICODE
    from sys import path
    from time import time
    from urlparse import parse_qs

    from earwigbot import bot, exceptions
    import oursql

    def get_results(lang, project, title, url, query):
        bot = bot.Bot(".earwigbot")
        try:
            site = bot.wiki.get_site(lang=lang, project=project)
        except exceptions.SiteNotFoundError:
            try:
                site = bot.wiki.add_site(lang=lang, project=project)
            except exceptions.APIError:
                return None, None

        page = site.get_page(title)                                                                                           # TODO: what if the page doesn't exist?
        # if url:
        #     result = get_url_specific_results(page, url)
        # else:
        #     conn = open_sql_connection(bot)
        #     if not query.get("nocache"):
        #         result = get_cached_results(page, conn)
        #     if query.get("nocache") or not result:
        #         result = get_fresh_results(page, conn)
        mc1 = __import__("earwigbot").wiki.copyvios.MarkovChain(page.get())
        mc2 = __import__("earwigbot").wiki.copyvios.MarkovChain("This is some random textual content for a page.")
        mci = __import__("earwigbot").wiki.copyvios.MarkovChainIntersection(mc1, mc2)
        result = __import__("earwigbot").wiki.copyvios.CopyvioCheckResult(
            True, 0.67123, "http://example.com/", 7, mc1, (mc2, mci))
        return page, result

    def get_url_specific_results(page, url):
        t_start = time()
        result = page.copyvio_compare(url)
        result.tdiff = time() - t_start
        return result

    def open_sql_connection(bot):
        conn_args = bot.config.wiki["_toolserverSQLCache"]
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
                block = [prev_prev, prev]  # Block for before
                alock = [prev, sword]  # Block for after
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
    query = parse_qs(environ["QUERY_STRING"])
    try:
        lang = query["lang"][0]
        project = query["project"][0]
        title = query["title"][0]
        url = query.get("url", [None])[0]
    except (KeyError, IndexError):
        page = None
    else:
        page, result = get_results(lang, project, title, url, query)
%>\
<%include file="/support/header.mako" args="environ=environ, title='Copyvio Detector', add_css=('copyvios.css',), add_js=('copyvios.js',)"/>
            <h1>Copyvio Detector</h1>
            <p>This tool attempts to detect <a href="//en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in articles. Simply give the title of the page you want to check and hit Submit. The tool will then search for its content elsewhere on the web and display a report if a similar webpage is found. If you provide a URL, it will not query any search engines and instead display a report comparing the article to that particular webpage, like the <a href="//toolserver.org/~dcoetzee/duplicationdetector/">Duplication Detector</a>. Check out the <a href="//en.wikipedia.org/wiki/User:EarwigBot/Copyvios/FAQ">FAQ</a> for more information and technical details.</p>
            <form action="${environ['PATH_INFO']}" method="get">
                <table>
                    <tr>
                        <td>Site:</td>
                        <td>
                            <select name="lang">
                                <option value="en" selected="selected">en (English)</option>
                            </select>
                            <select name="project">
                                <option value="wikipedia" selected="selected">Wikipedia</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <td>Page title:</td>
                        % if page:
                            <td><input type="text" name="title" size="60" value="${page.title() | h}" /></td>
                        % else:
                            <td><input type="text" name="title" size="60" /></td>
                        % endif
                    </tr>
                    <tr>
                        <td>URL:</td>
                        % if url:
                            <td><input type="text" name="url" size="120" value="${url | h}" /></td>
                        % else:
                            <td><input type="text" name="url" size="120" /></td>
                        % endif
                    </tr>
                    % if query.get("nocache") or page:
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
            % if page:
                <div class="divider"></div>
                <div id="cv-result-${'yes' if result.violation else 'no'}">
                    % if result.violation:
                        <h2 id="cv-result-header"><a href="${page.url()}">${page.title() | h}</a> is a suspected violation of <a href="${result.url | h}">${result.url | urlstrip}</a>.</h2>
                    % else:
                        <h2 id="cv-result-header">No violations detected in <a href="${page.url()}">${page.title() | h}</a>.</h2>
                    % endif
                    <ul id="cv-result-list">
                        <li><b><tt>${round(result.confidence * 100, 1)}%</tt></b> confidence of a violation.</li>
                        % if result.cached:
                            <li>Results are <a id="cv-cached" href="#">cached
                                <span>To save time (and money), this tool will retain the results of checks for up to 72 hours. This includes the URL of the "violated" source, but neither its content nor the content of the article. Future checks on the same page (assuming it remains unchanged) will not involve additional search queries, but a fresh comparison against the source URL will be made. If the page is modified, a new check will be run.</span>
                            </a> from ${result.cache_time} (${result.cache_age} ago). <a href="${environ['REQUEST_URI'] | h}&amp;nocache=1">Bypass the cache.</a></li>
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
