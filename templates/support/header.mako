<%page args="title, splash=False"/>\
<%!
    from flask import request, url_for
    from copyvios.background import get_background
    from copyvios.cookies import get_cookies
%>\
<%
    cookies = get_cookies()
%>\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>${title | h}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://tools-static.wmflabs.org/cdnjs/ajax/libs/oojs-ui/0.41.3/oojs-ui-core-wikimediaui.min.css" integrity="sha512-xL+tTXAo7a4IAwNrNqBcOGWSqJF6ip0jg4SEda2mapAUxPzfOZQ7inazR4TvSCblHQjwtTOkUDIFtnpaSrg3xg==" crossorigin="anonymous" referrerpolicy="no-referrer"/>
    <link rel="stylesheet" href="https://tools-static.wmflabs.org/cdnjs/ajax/libs/oojs-ui/0.41.3/oojs-ui-images-wikimediaui.min.css" integrity="sha512-A0LSCuOGH1+SyLhOs4eSKGbNgIEGXgIGh4ytb0GRj9GSUsjmmK6LFzB/E0o9ymRUvD+q7bZyv74XpboQt5qFvQ==" crossorigin="anonymous" referrerpolicy="no-referrer"/>
    <link rel="stylesheet" href="${request.script_root}${url_for('static', file='style.min.css')}"/>
    <script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="${request.script_root}${url_for('static', file='script.min.js')}"></script>
</head>
<% selected = cookies["CopyviosBackground"].value if "CopyviosBackground" in cookies else "list" %>\
% if selected == "plain":
    <body>
% else:
    <body onload="update_screen_size()" style="background-image: url('${get_background(selected) | h}');">
% endif
    <div id="container"${' class="splash"' if splash else ''}>
        <div id="content">
            <header>
                <h1><a href="/">Earwig&apos;s <strong>Copyvio Detector</strong></a></h1>
                <a id="settings-link" href="/settings">Settings</a>
            </header>
            <main>
