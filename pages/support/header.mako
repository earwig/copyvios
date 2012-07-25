<%page args="environ, cookies, title, slug=None, add_css=(), add_js=()"/>\
<%namespace name="index" file="/index.mako" import="get_tools"/>\
<%!
    from os import path
%>\
<%
    tools = get_tools()
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
        <title>${title} - earwig@toolserver</title>
        <link rel="stylesheet" href="${root}/static/css/main.css" type="text/css" />
        % for filename in add_css:
            <link rel="stylesheet" href="${root}/static/css/${filename}" type="text/css" />
        % endfor
        <script src="${root}/static/js/cookies.js" type="text/javascript"></script>
        <script src="${root}/static/js/potd.js" type="text/javascript"></script>
        % for filename in add_js:
            <script src="${root}/static/js/${filename}" type="text/javascript"></script>
        % endfor
    </head>
    % if "EarwigBackground" in cookies:
        % if cookies["EarwigBackground"].value == "list":
            <body onload="set_background_list()">
        % elif cookies["EarwigBackground"].value in ["plain-brown", "plain-blue"]:
            <body style="background-image: url('${root}/static/images/background-${cookies['EarwigBackground'].value[6:]}.png');">
        % else
            <body onload="set_background_potd()">
        % endif
    % else
        <body onload="set_background_potd()">
    % endif
        <div id="header">
            <p id="heading"><a class="dark" href="${pretty}">earwig</a><span class="light">@</span><a class="mid" href="https://wiki.toolserver.org/">toolserver</a><span class="light">:</span><a class="dark" href="${this}">${slug}</a></p>
            <p id="links"><span class="light">&gt;</span>
                % for num, tool in enumerate(tools, 1):
                    % if tool != "DIVIDER":
                        <% name, tool, link, complete, desc = tool %>
                        <abbr title="${name}${' (incomplete)' if not complete else ''}"><a class="${'dark' if complete else 'mid'}" href="${pretty}/${link}">${tool}</a></abbr>
                    % endif
                    % if num < len(tools):
                        <span class="light">&#124;</span>
                    % endif
                % endfor
            </p>
        </div>
        <div id="container">
