<%page args="environ, cookies, title"/>\
<%namespace module="copyvios.background" import="set_background"/>\
<%!
    from os import path
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
%>\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>${title}</title>
        <link rel="stylesheet" href="${root}/static/style.css" type="text/css" />
        <script src="${root}/static/script.js" type="text/javascript"></script>
    </head>
    <% selected = cookies["CopyviosBackground"].value if "CopyviosBackground" in cookies else "list" %>\
    % if selected == "plain":
        <body style="background-image: url('${root}/static/background.png');">
    % else:
        <body onload="update_screen_size()" style="background-image: url('${set_background(cookies, selected) | h}'); background-size: cover;">
    % endif
        <div id="header">
            <table id="heading">
                <tr>
                    <td id="head-home"><a id="a-home" href="${root}">Earwig's Copyvio Detector</a></td>
                    <td id="head-settings"><a id="a-settings" href="${root}/settings">Settings</a></td>
                </tr>
            </table>
        </div>
        <div id="container">
