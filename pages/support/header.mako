<%page args="environ, cookies, title, slug=None, add_css=(), add_js=()"/>\
<%namespace module="copyvios.background" import="set_background"/>\
<%!
    from os import path
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
    this = environ["PATH_INFO"]
    pretty = path.split(root)[0]
    if not slug:
        slug = path.split(this)[1]
        if slug.endswith(".fcgi"):
            slug = slug[:-5]
%>\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en-us">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>${title}</title>
        <link rel="stylesheet" href="${root}/static/style.css" type="text/css" />
        <script src="${root}/static/script.js" type="text/javascript"></script>
    </head>
    <% selected = cookies["CopyviosBackground"].value if "CopyviosBackground" in cookies else "plain" %>\
    % if selected == "plain":
        <body style="background-image: url('${root}/static/background.png');">
    % else:
        <% bg_url = set_background(cookies, selected) %>\
        <body onload="update_screen_size()" style="background-image: url('${bg_url | h}'); background-size: cover;">
    % endif
        <div id="header">
            <p id="heading"><a class="dark" href="${pretty}">earwig</a><span class="light">@</span><a class="mid" href="https://wiki.toolserver.org/">toolserver</a><span class="light">:</span><a class="dark" href="${this}">${slug}</a></p>
            <p id="links"><span class="light">&gt;</span>
                % for num, tool in enumerate(tools, 1):
                    % if tool != "DIVIDER":
                        <% name, tool, link, complete, desc = tool %>\
                        <abbr title="${name}${' (incomplete)' if not complete else ''}"><a class="${'dark' if complete else 'mid'}" href="${pretty}/${link}">${tool}</a></abbr>
                    % endif
                    % if num < len(tools):
                        <span class="light">&#124;</span>
                    % endif
                % endfor
            </p>
        </div>
        <div id="container">
