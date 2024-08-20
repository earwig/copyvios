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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://tools-static.wmflabs.org/cdnjs/ajax/libs/oojs-ui/0.41.3/oojs-ui-wikimediaui.min.css" integrity="sha512-NfHDuNXQxgngdmLBodQLDR2DAkT+hFpALuQv4TvRXC2AiDklxQHji6+KCFMrR/EOrUpaq30yc4CMP+aQ39kwXA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <link rel="stylesheet" href="${request.script_root}${url_for('static', file='style.min.css')}"/>
    <script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="${request.script_root}${url_for('static', file='script.min.js')}"></script>
</head>
<% selected = g.cookies["CopyviosBackground"].value if "CopyviosBackground" in g.cookies else "list" %>
% if selected == "plain":
    <body>
% else:
    <body onload="updateScreenSize()" style="background-image: url('${set_background(selected) | h}');">
% endif
    <div id="container"${' class="splash"' if splash else ''}>
        <div id="content">
            <header>
                <h1><a href="/">Earwig&apos;s <strong>Copyvio Detector</strong></a></h1>
                <a id="settings-link" href="/settings">Settings</a>
            </header>
            <main>
