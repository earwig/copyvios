<%include file="/support/header.mako" args="environ=environ, cookies=cookies, title='EarwigBot Status'"/>\
<%namespace module="toolserver.earwigbot" import="collect_status_info"/>\
<%def name="get_status()" filter="trim">
    <% status, since, uptime, host = collect_status_info() %>
    ${"has been" if status == "online" else "is"} <span class="${status}">${status}</span>
    % if status == "online":
        since ${since} (${uptime} uptime) on <tt>${host}</tt>
    % endif
</%def>\
            <h1>EarwigBot Status</h1>
            <p>EarwigBot ${get_status()}.</p>
            <p>Additional information: <a href="http://status.toolserver.org/">status.toolserver.org</a></p>
<%include file="/support/footer.mako" args="environ=environ, cookies=cookies"/>
