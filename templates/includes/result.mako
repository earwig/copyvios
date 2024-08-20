<%!
    from flask import request
    from copyvios.attribution import get_attribution_info
    from copyvios.checker import T_POSSIBLE, T_SUSPECT
%>
<%namespace module="copyvios.highlighter" import="highlight_delta"/>
<%namespace module="copyvios.misc" import="get_permalink, httpsfix, urlstrip"/>
<div id="generation-time">
    Results
    % if result.cached:
        <span class="tooltip-anchor-inline">cached<span class="tooltip tooltip-align-center"><span>To save time (and money), this tool will retain the results of checks for up to 72 hours. This includes the URLs of the checked sources, but neither their content nor the content of the article. Future checks on the same page (assuming it remains unchanged) will not involve additional search queries, but a fresh comparison against the source URL will be made. If the page is modified, a new check will be run.</span></span></span> from <abbr title="${result.cache_time}">${result.cache_age} ago</abbr>. Originally
    % endif
    generated in <span class="mono">${round(result.time, 3)}</span>
    % if query.action == "search":
        seconds using <span class="mono">${result.queries}</span> quer${"y" if result.queries == 1 else "ies"}.
    % else:
        seconds.
    % endif
    <a href="${ get_permalink(query) | h}">Permalink.</a>
</div>

<div id="cv-result" class="${'red' if result.confidence >= T_SUSPECT else 'yellow' if result.confidence >= T_POSSIBLE else 'green'}-box">
    <table id="cv-result-head-table">
        <colgroup>
            <col>
            <col>
            <col>
        </colgroup>
        <tr>
            <td>
                <a href="${query.page.url}">${query.page.title | h}</a>
                % if query.oldid:
                    @<a href="https://${query.site.domain | h}/w/index.php?oldid=${query.oldid | h}">${query.oldid | h}</a>
                % endif
                % if query.redirected_from:
                    <br />
                    <span id="redirected-from">Redirected from <a href="https://${query.site.domain | h}/w/index.php?title=${query.redirected_from.title | u}&amp;redirect=no">${query.redirected_from.title | h}</a>. <a href="${request.url | httpsfix, h}&amp;noredirect=1">Check original.</a></span>
                % endif
            </td>
            <td>
                <div>
                    % if result.confidence >= T_SUSPECT:
                        Violation suspected
                    % elif result.confidence >= T_POSSIBLE:
                        Violation possible
                    % elif result.sources:
                        Violation unlikely
                    % else:
                        No violation
                    % endif
                </div>
                <div>${int(round(result.confidence * 100))}%</div>
                <div>similarity</div>
            </td>
            <td>
                % if result.url:
                    <a href="${result.url | h}">${result.url | urlstrip, h}</a>
                    % if len(result.included_sources) == 2:
                        <br>and <a href="${result.included_sources[1].url | h}">${result.included_sources[1].url | urlstrip, h}</a>
                    % elif len(result.included_sources) > 2:
                        <br>and ${len(result.included_sources) - 1} other sources
                    % endif
                % else:
                    <span id="result-head-no-sources">No matches found.</span>
                % endif
            </td>
        </tr>
    </table>
</div>

<% attrib = get_attribution_info(query.site, query.page) %>
% if attrib:
    <div id="attribution-warning" class="yellow-box">
        This article contains an attribution template: <code>{{<a href="${attrib[1]}">${attrib[0] | h}</a>}}</code>. Please verify that any potential copyvios are not from properly attributed sources.
    </div>
% endif

% if query.turnitin_result:
    <div id="turnitin-container" class="${'red' if query.turnitin_result.reports else 'green'}-box">
        <div id="turnitin-title">Turnitin Results</div>
        % if query.turnitin_result.reports:
            <table id="turnitin-table"><tbody>
            % for report in turnitin_result.reports:
                <tr><td class="turnitin-table-cell"><a href="https://eranbot.toolforge.org/ithenticate.py?rid=${report.reportid}">Report ${report.reportid}</a> for text added at <a href="https://${query.lang}.wikipedia.org/w/index.php?title=${query.title}&amp;diff=${report.diffid}"> ${report.time_posted.strftime("%H:%M, %d %B %Y (UTC)")}</a>:
                <ul>
                % for source in report.sources:
                      <li>${source['percent']}% of revision text (${source['words']} words) found at <a href="${source['url'] | h}">${source['url'] | h}</a></li>
                % endfor
                </ul></td></tr>
            % endfor
            </tbody></table>
        % else:
            <div id="turnitin-summary">No matching sources found.</div>
        % endif
    </div>
% endif

% if query.action == "search" or len(result.sources) > 1:
    <% skips = False %>
    <div id="sources-container">
        <div id="sources-title">Checked sources</div>
        % if result.sources:
            <table id="cv-result-sources">
                </colgroup>
                <tr>
                    <th>#</th>
                    <th>URL</th>
                    <th>Similarity</th>
                    <th>Actions</th>
                </tr>
                % for i, source in enumerate(result.sources):
                    <tr class="source-row ${"source-default-hidden" if i >= 10 else "source-row-selected" if i == 0 else ""}" data-id="${i + 1}">
                        <td>
                            % if i < len(result.included_sources):
                                <a class="source-num source-num-included cv-hl cv-hl-${i + 1}" href="#" title="Toggle highlighting" data-id="${i + 1}">${i + 1}</a>
                            % else:
                                <span class="source-num">${i + 1}</span>
                            % endif
                        </td>
                        <td>
                            <a class="source-url source-url-${i + 1}" href="${source.url | h}" data-domain="${source.domain or '' | h}">${source.url | h}</a>
                        </td>
                        <td>
                            % if source.excluded:
                                <span class="source-excluded">Excluded</span>
                            % elif source.skipped:
                                <% skips = True %>
                                <span class="source-skipped">Skipped</span>
                            % else:
                                <span class="source-similarity ${"source-suspect" if source.confidence >= T_SUSPECT else "source-possible" if source.confidence >= T_POSSIBLE else "source-novio"}">${int(round(source.confidence * 100))}%</span>
                            % endif
                        </td>
                        <td>
                            <ul class="hlist">
                                % if i < len(result.included_sources):
                                    <li>
                                        <a class="source-compare" href="#" title="View this source" data-id="${i + 1}">Select</a>
                                        <strong class="source-compare-selected">Select</strong>
                                    </li>
                                % endif
                                <li>
                                    <a href="${request.script_root | h}/?lang=${query.lang | h}&amp;project=${query.project | h}&amp;oldid=${query.oldid or query.page.lastrevid | h}&amp;action=compare&amp;url=${source.url | u}" title="Open a direct comparison to this source">Open</a>
                                </li>
                            </ul>
                        </td>
                    </tr>
                % endfor
            </table>
        % else:
            <div class="cv-source-footer">
                No sources checked.
            </div>
        % endif
        % if len(result.sources) > 10:
            <div id="cv-additional" class="cv-source-footer">
                ${len(result.sources) - 10} URL${"s" if len(result.sources) > 11 else ""} with lower similarity hidden. <a id="show-additional-sources" href="#">Show them.</a>
            </div>
        % endif
        % if skips or result.possible_miss:
            <div class="cv-source-footer">
                The search ended early because a match was found with high similarity. <a href="${request.url | httpsfix, h}&amp;noskip=1">Do a complete check.</a>
            </div>
        % endif
    </div>
% endif
<div id="source-tooltips"></div>
<table class="cv-chain-table">
    <tr>
        <td class="cv-chain-article">
            Article:
        </td>
        % for i, source in enumerate(result.included_sources, 1):
            <td class="cv-chain-source cv-chain-source-${i} ${"hidden" if i > 1 else ""}">
                Source${" %s (%s)" % (i, source.domain or source.url) if len(result.included_sources) > 1 else "" | h}:
            </td>
        % endfor
    </tr>
    <tr>
        <td class="cv-chain-cell cv-chain-article">
            <div><p>${highlight_delta(result.article_chain, [source.chains[1] for source in result.included_sources])}</p></div>
        </td>
        <td class="cv-chain-cell cv-chain-source cv-chain-source-1">
            <div><p>${highlight_delta(result.best.chains[0], result.best.chains[1]) if result.best else ""}</p></div>
        </td>
        % for i, source in enumerate(result.included_sources[1:], 2):
            <td class="cv-chain-cell cv-chain-source cv-chain-source-${i} hidden">
                <div><p>${highlight_delta(source.chains[0], source.chains[1], index=i)}</p></div>
            </td>
        % endfor
    </tr>
</table>
