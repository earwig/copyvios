<%page args="title, splash=False"/>\
<%!
    from flask import g, request, url_for
    from copyvios.background import set_background
%>\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>${title | h}</title>
    <link rel="stylesheet" href="${request.script_root}${url_for('static', file='style.min.css')}"/>
    <script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="${request.script_root}${url_for('static', file='script.min.js')}"></script>
</head>
<% selected = g.cookies["CopyviosBackground"].value if "CopyviosBackground" in g.cookies else "list" %>\
% if selected == "plain":
    <body>
% else:
    <body onload="update_screen_size()" style="background-image: url('${set_background(selected) | h}');">
% endif
    <div id="container"${' class="splash"' if splash else ''}>
        <div id="content">
            <header>
                <h1><a href="/">Earwig&apos;s <strong>Copyvio Detector</strong></a></h1>
                <a id="settings-link" href="/settings">Settings</a>
            </header>
            <main>
