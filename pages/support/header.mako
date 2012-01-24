<%page args="environ, title, slug=None"/>\
<%!
    from os import path
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
    this = environ["PATH_INFO"]
    pretty = path.split(root)[0]
    if not slug:
        slug = path.split(this)[1]
%>\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en-us">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>${title} - earwig@toolserver</title>
        <link rel="stylesheet" href="${root}/static/css/main.css" type="text/css" />
    </head>
    <body>
        <div id="header">
            <h1 id="head"><a class="dark" href="${pretty}">earwig</a><span class="light">@</span><a class="mid" href="http://wiki.toolserver.org/">toolserver</a><span class="light">:</span><a class="dark" href="${this}">${slug}</a></h1>
            <h2 id="links"><span class="light">&gt;</span> <a class="dark" href="${pretty}/index">home</a> <span class="light">&#124;</span> <a class="dark" href="${pretty}/copyvios">copyvios</a></h2> 
        </div>
        <div id="container">