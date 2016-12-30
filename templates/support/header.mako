<%page args="title"/>\
<%!
    from flask import g, request, url_for
    from copyvios.background import set_background
%>\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>${title}</title>
        <link rel="stylesheet" href="${request.script_root}${url_for('static', file='style.min.css')}" type="text/css" />
        <script src="//code.jquery.com/jquery-1.11.1.min.js" type="text/javascript"></script>
        <script src="${request.script_root}${url_for('static', file='script.min.js')}" type="text/javascript"></script>
    </head>
    <% selected = g.cookies["CopyviosBackground"].value if "CopyviosBackground" in g.cookies else "list" %>\
    % if selected == "plain":
        <body style="background-image: url('${request.script_root}/static/background.png');">
    % else:
        <body onload="update_screen_size()" style="background-image: url('${set_background(selected) | h}'); background-size: cover;">
    % endif
        <div id="header">
            <table id="heading">
                <tr>
                    <td id="head-home"><a id="a-home" href="${request.script_root}">Earwig's Copyvio Detector</a></td>
                    <td id="head-settings"><a id="a-settings" href="${request.script_root}/settings">Settings</a></td>
                </tr>
            </table>
        </div>
        <div id="container">
