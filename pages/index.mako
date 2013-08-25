<%!
    from os import path

    tools = [
        ("Home", "home", "index", True, None),
        ("Settings", "settings", "settings", True, None),
        ("DIVIDER"),
        ("Copyvio Detector", "copyvios", "copyvios", True,
            'Try to detect <a href="//en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in articles by searching the web for page content, or compare an article to a specific URL.'),
    ]
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
    pretty = path.split(root)[0]
%>\
<%def name="get_tools()"><% return tools %></%def>\
<%include file="/support/header.mako" args="environ=environ, cookies=cookies, title='Home', slug='home'"/>
            <h1>My Tools</h1>
            % for tool in tools:
                % if tool != "DIVIDER":
                    <% name, tool, link, complete, desc = tool %>
                    % if desc:
                        <div class="toolbox">
                            <p class="toolname"><a class="dark" href="${pretty}/${link}"><span class="medium">${tool}:</span> ${name}</a></p>
                            <p class="tooldesc">${desc}</p>
                        </div>
                    % endif
                % endif
            % endfor
<%include file="/support/footer.mako" args="environ=environ, cookies=cookies"/>
