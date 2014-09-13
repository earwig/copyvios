<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>API - Earwig's Copyvio Detector</title>
        <link rel="stylesheet" href="${request.script_root}/static/api.min.css" type="text/css" />
    </head>
    <body>
        % if help:
            <div id="help">
                <p>This is the first version of the <a href="//en.wikipedia.org/wiki/Application_programming_interface">API</a> for <a href="${request.script_root}">Earwig's Copyvio Detector</a>. It works, but some bugs might still need to be ironed out, so please <a href="https://github.com/earwig/copyvios/issues">report any</a> if you see them.</p>
            </div>
        % endif
        % if result:
            <div id="result">
                <p>You are using <span class="code">jsonfm</span> output mode, which renders JSON data as a formatted HTML document. This is intended for testing and debugging only.</p>
                <!-- walk tree -->
            </div>
        % endif
    </body>
</html>
