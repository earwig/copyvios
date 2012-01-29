<%!
    from os import path
    import time

    tools = [
        ("Home", "home", "index", True, None),
        ("Copyvio Detector", "copyvios", "copyvios", True, "Blah"),
        ("EarwigBot Status", "earwigbot", "earwigbot", True, "Blah"),
        ("File Extension Checker", "extensions", "extensions", False, "Blah"),
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
            % for name, tool, link, complete, desc in tools:
                % if desc:
                    <div class="toolbox">
                        <p class="toolname"><a class="dark" href="${pretty}/${link}"><span class="medium">${tool}:</span> ${name}</a></p>
                        <p class="tooldesc">${desc}</p>
                    </div>
                % endif
            % endfor
<%include file="/support/footer.mako" args="environ=environ"/>
