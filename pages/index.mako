<%include file="/support/header.mako" args="environ=environ, cookies=cookies, title='Earwig\'s Copyvio Detector'"/>\
<%namespace module="copyvios" import="main, highlight_delta"/>\
<%namespace module="copyvios.misc" import="urlstrip"/>\
<%
    query = main(environ)
    # Unpack query data:
    lang, orig_lang, title, oldid, url, nocache = query.lang, query.orig_lang, query.title, query.oldid, query.url, query.nocache
    bot, site, page, result = query.bot, query.site, query.page, query.result
%>\
            % if query.project and lang and (title or oldid):
                % if not site:
                    <div id="info-box" class="red-box">
                        <p>The given site (project=<b><span class="mono">${query.project | h}</span></b>, language=<b><span class="mono">${lang | h}</span></b>) doesn't seem to exist. It may also be closed or private. <a href="//${lang | h}.${query.project | h}.org/">Confirm its URL.</a></p>
                    </div>
                % elif title and not result:
                    <div id="info-box" class="red-box">
                        <p>The given page doesn't seem to exist: <a href="${page.url}">${page.title | h}</a>.</p>
                    </div>
                % elif oldid and not result:
                    <div id="info-box" class="red-box">
                        <p>The given revision ID doesn't seem to exist: <a href="//${site.domain | h}/w/index.php?oldid=${oldid | h}">${oldid | h}</a>.</p>
                    </div>
                % elif url and result == "bad URI":
                    <% result = None %>
                    <div id="info-box" class="red-box">
                        <p>Unsupported URI scheme: <a href="${url | h}">${url | h}</a>.</p>
                    </div>
                % endif
            %endif
            <p>This tool attempts to detect <a href="//en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in articles. Simply give the title of the page or ID of the revision you want to check and hit Submit. The tool will search for similar content elsewhere on the web and display a report if a match is found. If you also provide a URL, it will not query any search engines and instead display a report comparing the article to that particular webpage, like the <a href="//toolserver.org/~dcoetzee/duplicationdetector/">Duplication Detector</a>. Check out the <a href="//en.wikipedia.org/wiki/User:EarwigBot/Copyvios/FAQ">FAQ</a> for more information and technical details.</p>
            <p><i>Note:</i> The tool is still in beta. You are completely welcome to use it and provide <a href="//en.wikipedia.org/wiki/User_talk:The_Earwig">feedback</a>, but be aware that it may produce strange or broken results.</p>
            <form action="${environ['REQUEST_URI']}" method="get">
                <table id="cv-form">
                    <tr>
                        <td>Site:</td>
                        <td colspan="3">
                            <span class="mono">http://</span>
                            <select name="lang">
                                <% selected_lang = orig_lang if orig_lang else cookies["CopyviosDefaultLang"].value if "CopyviosDefaultLang" in cookies else bot.wiki.get_site().lang %>\
                                % for code, name in query.all_langs:
                                    % if code == selected_lang:
                                        <option value="${code | h}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code | h}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                            <span class="mono">.</span>
                            <select name="project">
                                <% selected_project = query.project if query.project else cookies["CopyviosDefaultProject"].value if "CopyviosDefaultProject" in cookies else bot.wiki.get_site().project %>\
                                % for code, name in query.all_projects:
                                    % if code == selected_project:
                                        <option value="${code | h}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code | h}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                            <span class="mono">.org</span>
                        </td>
                    </tr>
                    <tr>
                        <td id="cv-col1">Page&nbsp;title:</td>
                        <td id="cv-col2">
                            % if page:
                                <input class="cv-text" type="text" name="title" value="${page.title | h}" />
                            % elif title:
                                <input class="cv-text" type="text" name="title" value="${title | h}" />
                            % else:
                                <input class="cv-text" type="text" name="title" />
                            % endif
                        </td>
                        <td id="cv-col3">or&nbsp;revision&nbsp;ID:</td>
                        <td id="cv-col4">
                            % if oldid:
                                <input class="cv-text" type="text" name="oldid" value="${oldid | h}" />
                            % else:
                                <input class="cv-text" type="text" name="oldid" />
                            % endif
                        </td>
                    </tr>
                    <tr>
                        <td>URL&nbsp;(optional):</td>
                        <td colspan="3">
                            % if url:
                                <input class="cv-text" type="text" name="url" value="${url | h}" />
                            % else:
                                <input class="cv-text" type="text" name="url" />
                            % endif
                        </td>
                    </tr>
                    % if nocache or (result and result.cached):
                        <tr>
                            <td>Bypass&nbsp;cache:</td>
                            <td colspan="3">
                                % if nocache:
                                    <input type="checkbox" name="nocache" value="1" checked="checked" />
                                % else:
                                    <input type="checkbox" name="nocache" value="1" />
                                % endif
                            </td>
                        </tr>
                    % endif
                    <tr>
                        <td colspan="4">
                            <button type="submit">Submit</button>
                        </td>
                    </tr>
                </table>
            </form>
            % if result:
                <% show_details = "CopyviosShowDetails" in cookies and cookies["CopyviosShowDetails"].value == "True" %>
                <div class="divider"></div>
                <div id="cv-result" class="${'red' if result.violation else 'green'}-box">
                    % if result.violation:
                        <h2 id="cv-result-header"><a href="${page.url}">${page.title | h}</a> is a suspected violation of <a href="${result.url | h}">${result.url | urlstrip, h}</a>.</h2>
                    % else:
                        <h2 id="cv-result-header">No violations detected in <a href="${page.url}">${page.title | h}</a>.</h2>
                    % endif
                    <ul id="cv-result-list">
                        % if not result.violation and not url:
                            % if result.url:
                                <li>Best match: <a href="${result.url | h}">${result.url | urlstrip, h}</a>.</li>
                            % else:
                                <li>No matches found.</li>
                            % endif
                        % endif
                        <li><b><span class="mono">${round(result.confidence * 100, 1)}%</span></b> confidence of a violation.</li>
                        % if result.cached:
                            <li>Results are <a id="cv-cached" href="#">cached
                                <span>To save time (and money), this tool will retain the results of checks for up to 72 hours. This includes the URL of the "violated" source, but neither its content nor the content of the article. Future checks on the same page (assuming it remains unchanged) will not involve additional search queries, but a fresh comparison against the source URL will be made. If the page is modified, a new check will be run.</span>
                            </a> from ${result.cache_time} (${result.cache_age} ago). <a href="${environ['REQUEST_URI'] | h}&amp;nocache=1">Bypass the cache.</a></li>
                        % else:
                            <li>Results generated in <span class="mono">${round(result.time, 3)}</span> seconds using <span class="mono">${result.queries}</span> queries.</li>
                        % endif
                        <li><a id="cv-result-detail-link" href="#cv-result-detail" onclick="copyvio_toggle_details()">${"Hide" if show_details else "Show"} details:</a></li>
                    </ul>
                    <div id="cv-result-detail" style="display: ${'block' if show_details else 'none'};">
                        <ul id="cv-result-detail-list">
                            <li>Trigrams: <i>Article:</i> <span class="mono">${result.article_chain.size()}</span> / <i>Source:</i> <span class="mono">${result.source_chain.size()}</span> / <i>Delta:</i> <span class="mono">${result.delta_chain.size()}</span></li>
                            % if result.cached:
                                % if result.queries:
                                    <li>Retrieved from cache in <span class="mono">${round(result.time, 3)}</span> seconds (originally generated in <span class="mono">${round(result.original_time, 3)}</span>s using <span class="mono">${result.queries}</span> queries; <span class="mono">${round(result.original_time - result.time, 3)}</span>s saved).</li>
                                % else:
                                    <li>Retrieved from cache in <span class="mono">${round(result.time, 3)}</span> seconds (originally generated in <span class="mono">${round(result.original_time, 3)}</span>s; <span class="mono">${round(result.original_time - result.time, 3)}</span>s saved).</li>
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
