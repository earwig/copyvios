<%!
    from os import path

    tools = [
        ("Home", "home", "index", True, None),
        ("Settings", "settings", "settings", True, None),
        ("DIVIDER"),
        ("Copyvio Detector", "copyvios", "copyvios", True, "Blah"),
        ("EarwigBot Status", "earwigbot", "earwigbot", True, "Blah"),
        ("Contribution Surveyor", "surveyor", "surveyor", False, "Blah"),
        ("SWMT Helper", "swmt", "swmt", False, "Blah"),
    ]
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
    pretty = path.split(root)[0]
%>\
<%def name="get_tools()"><% return tools %></%def>\
<%include file="/support/header.mako" args="environ=environ, title='Home', slug='home'"/>
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
<%include file="/support/footer.mako" args="environ=environ"/>
