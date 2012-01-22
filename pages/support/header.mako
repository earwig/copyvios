<%page args="environ, title"/>\
<%!
    from os import path
%>\
<% root = path.dirname(environ["SCRIPT_NAME"]) %>\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en-us">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>${title} - earwig@toolserver</title>
        <link rel="stylesheet" href="${root}/static/css/main.css" type="text/css" />
    </head>
    <body>
        <div id="container">