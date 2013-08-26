<%page args="environ, cookies, title"/>\
<%namespace module="copyvios.background" import="set_background"/>\
<%!
    from os import path
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
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
            <p id="heading"><a class="dark" href="${root}">Earwig's Copyvio Detector</a></p>
            <p id="links"><a class="mid" href="${root}/settings">Settings</a></p>
        </div>
        <div id="container">
