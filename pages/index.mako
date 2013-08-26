<%include file="/support/header.mako" args="environ=environ, cookies=cookies, title='Earwig's Copyvio Detector'"/>\
<%namespace module="copyvios" import="main, highlight_delta"/>\
<%namespace module="copyvios.misc" import="urlstrip"/>\
<% query, bot, all_langs, all_projects, page, result = main(environ) %>\
            % if query.project and query.lang and query.title and not page:
                <div class="red-box">
                    <p>The given site (project=<b><tt>${query.project | h}</tt></b>, language=<b><tt>${query.lang | h}</tt></b>) doesn't seem to exist. It may also be closed or private. <a href="//${query.lang | h}.${query.project | h}.org/">Confirm its URL.</a></p>
                </div>
            % elif query.project and query.lang and query.title and page and not result:
                <div class="red-box">
                    <p>The given page doesn't seem to exist: <a href="${page.url}">${page.title | h}</a>.</p>
                </div>
            % elif query.project and query.lang and query.title and query.url and page and result == "bad URI":
                <% result = None %>
                <div class="red-box">
                    <p>Unsupported URI scheme: <a href="${query.url | h}">${query.url | h}</a>.</p>
                </div>
            % endif
            <p>This tool attempts to detect <a href="//en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in articles. Simply give the title of the page you want to check and hit Submit. The tool will then search for its content elsewhere on the web and display a report if a similar webpage is found. If you also provide a URL, it will not query any search engines and instead display a report comparing the article to that particular webpage, like the <a href="//toolserver.org/~dcoetzee/duplicationdetector/">Duplication Detector</a>. Check out the <a href="//en.wikipedia.org/wiki/User:EarwigBot/Copyvios/FAQ">FAQ</a> for more information and technical details.</p>
            <p><i>Note:</i> The tool is still in beta. You are completely welcome to use it and provide <a href="//en.wikipedia.org/wiki/User_talk:The_Earwig">feedback</a>, but be aware that it may produce strange or broken results.</p>
            <form action="${environ['PATH_INFO']}" method="get">
                <table>
                    <tr>
                        <td>Site:</td>
                        <td>
                            <tt>http://</tt>
                            <select name="lang">
                                <% selected_lang = query.orig_lang if query.orig_lang else cookies["CopyviosDefaultLang"].value if "CopyviosDefaultLang" in cookies else bot.wiki.get_site().lang %>\
                                % for code, name in all_langs:
                                    % if code == selected_lang:
                                        <option value="${code | h}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code | h}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                            <tt>.</tt>
                            <select name="project">
                                <% selected_project = query.project if query.project else cookies["CopyviosDefaultProject"].value if "CopyviosDefaultProject" in cookies else bot.wiki.get_site().project %>\
                                % for code, name in all_projects:
                                    % if code == selected_project:
                                        <option value="${code | h}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code | h}">${name}</option>
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
                        % elif query.title:
                            <td><input type="text" name="title" size="60" value="${query.title | h}" /></td>
                        % else:
                            <td><input type="text" name="title" size="60" /></td>
                        % endif
                    </tr>
                    <tr>
                        <td>URL (optional):</td>
                        % if query.url:
                            <td><input type="text" name="url" size="120" value="${query.url | h}" /></td>
                        % else:
                            <td><input type="text" name="url" size="120" /></td>
                        % endif
                    </tr>
                    % if query.nocache or (result and result.cached):
                        <tr>
                            <td>Bypass cache:</td>
                            % if query.nocache:
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
            % if page and result:
                <div class="divider"></div>
                <div id="cv-result-${'yes' if result.violation else 'no'}">
                    % if result.violation:
                        <h2 id="cv-result-header"><a href="${page.url}">${page.title | h}</a> is a suspected violation of <a href="${result.url | h}">${result.url | urlstrip, h}</a>.</h2>
                    % else:
                        <h2 id="cv-result-header">No violations detected in <a href="${page.url}">${page.title | h}</a>.</h2>
                    % endif
                    <ul id="cv-result-list">
                        % if not result.violation and not query.url:
                            % if result.url:
                                <li>Best match: <a href="${result.url | h}">${result.url | urlstrip, h}</a>.</li>
                            % else:
                                <li>No matches found.</li>
                            % endif
                        % endif
                        <li><b><tt>${round(result.confidence * 100, 1)}%</tt></b> confidence of a violation.</li>
                        % if result.cached:
                            <li>Results are <a id="cv-cached" href="#">cached
                                <span>To save time (and money), this tool will retain the results of checks for up to 72 hours. This includes the URL of the "violated" source, but neither its content nor the content of the article. Future checks on the same page (assuming it remains unchanged) will not involve additional search queries, but a fresh comparison against the source URL will be made. If the page is modified, a new check will be run.</span>
                            </a> from ${result.cache_time} (${result.cache_age} ago). <a href="${environ['REQUEST_URI'] | h}&amp;nocache=1">Bypass the cache.</a></li>
                        % else:
                            <li>Results generated in <tt>${round(result.time, 3)}</tt> seconds using <tt>${result.queries}</tt> queries.</li>
                        % endif
                        % if "CopyviosShowDetails" in cookies and cookies["CopyviosShowDetails"].value == "True":
                            <li><a id="cv-result-detail-link" href="#cv-result-detail" onclick="copyvio_toggle_details()">Hide details:</a></li>
                        % else:
                            <li><a id="cv-result-detail-link" href="#cv-result-detail" onclick="copyvio_toggle_details()">Show details:</a></li>
                        % endif
                    </ul>
                    % if "CopyviosShowDetails" in cookies and cookies["CopyviosShowDetails"].value == "True":
                        <div id="cv-result-detail" style="display: block;">
                    % else:
                        <div id="cv-result-detail" style="display: none;">
                    % endif
                        <ul id="cv-result-detail-list">
                            <li>Trigrams: <i>Article:</i> <tt>${result.article_chain.size()}</tt> / <i>Source:</i> <tt>${result.source_chain.size()}</tt> / <i>Delta:</i> <tt>${result.delta_chain.size()}</tt></li>
                            % if result.cached:
                                % if result.queries:
                                    <li>Retrieved from cache in <tt>${round(result.time, 3)}</tt> seconds (originally generated in <tt>${round(result.original_time, 3)}</tt>s using <tt>${result.queries}</tt> queries; <tt>${round(result.original_time - result.time, 3)}</tt>s saved).</li>
                                % else:
                                    <li>Retrieved from cache in <tt>${round(result.time, 3)}</tt> seconds (originally generated in <tt>${round(result.original_time, 3)}</tt>s; <tt>${round(result.original_time - result.time, 3)}</tt>s saved).</li>
                                % endif
                            % endif
                            % if result.queries:
                                <li><i>Fun fact:</i> The Wikimedia Foundation paid Yahoo! Inc. <a href="http://info.yahoo.com/legal/us/yahoo/search/bosspricing/details.html">$${result.queries * 0.0008} USD</a> for these results.</li>
                            % endif
                        </ul>
                        <table id="cv-chain-table">
                            <tr>
                                <td class="cv-chain-cell">Article: <div class="cv-chain-detail"><p>${highlight_delta(result.article_chain, result.delta_chain)}</p></div></td>
                                <td class="cv-chain-cell">Source: <div class="cv-chain-detail"><p>${highlight_delta(result.source_chain, result.delta_chain)}</p></div></td>
                            </tr>
                        </table>
                    </div>
                </div>
            % endif
<%include file="/support/footer.mako" args="environ=environ, cookies=cookies"/>
