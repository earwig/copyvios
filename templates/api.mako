<%def name="walk_json(obj)">
    <!-- TODO -->
    ${obj | h}
</%def>
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
                <h1>Copyvio Detector API</h1>
                <p>This is the first version of the <a href="//en.wikipedia.org/wiki/Application_programming_interface">API</a> for <a href="${request.script_root}">Earwig's Copyvio Detector</a>. It works, but some bugs might still need to be ironed out, so please <a href="https://github.com/earwig/copyvios/issues">report any</a> if you see them.</p>
                <h2>Requests</h2>
                <p>The API responds to GET requests made to <span class="code">https://tools.wmflabs.org/copyvios/api.json</span>. Parameters are described in the tables below:</p>
                <table class="parameters">
                    <tr>
                        <th colspan="4">Always</th>
                    </tr>
                    <tr>
                        <th>Parameter</th>
                        <th>Values</th>
                        <th>Required?</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>action</td>
                        <td><span class="code">compare</span>, <span class="code">search</span>, <span class="code">sites</span></td>
                        <td>Yes</td>
                        <td>The API will do URL comparisons in <span class="code">compare</span> mode, run full copyvio checks in <span class="code">search</span> mode, and list all known site languages and projects in <span class="code">sites</span> mode.</td>
                    </tr>
                    <tr>
                        <td>format</td>
                        <td><span class="code">json</span>, <span class="code">jsonfm</span></td>
                        <td>No&nbsp;(default:&nbsp;<span class="code">json</span>)</td>
                        <td>The default output format is <a href="http://json.org/">JSON</a>. <span class="code">jsonfm</span> mode produces the same output, but renders it as a formatted HTML document for debugging.</td>
                    </tr>
                    <tr>
                        <td>version</td>
                        <td>integer</td>
                        <td>No (default: <span class="code">1</span>)</td>
                        <td>Currently, the API only has one version. You can skip this parameter, but it is recommended to include it for forward compatibility.</td>
                    </tr>
                </table>
                <table class="parameters">
                    <tr>
                        <th colspan="4"><span class="code">compare</span> Mode</th>
                    </tr>
                    <tr>
                        <th>Parameter</th>
                        <th>Values</th>
                        <th>Required?</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>project</td>
                        <td>string</td>
                        <td>Yes</td>
                        <td>The project code of the site the page lives on. Examples are <span class="code">wikipedia</span> and <span class="code">wiktionary</span>. A list of acceptable values can be retrieved using <span class="code">action=sites</span>.</td>
                    </tr>
                    <tr>
                        <td>lang</td>
                        <td>string</td>
                        <td>Yes</td>
                        <td>The language code of the site the page lives on. Examples are <span class="code">en</span> and <span class="code">de</span>. A list of acceptable values can be retrieved using <span class="code">action=sites</span>.</td>
                    </tr>
                    <tr>
                        <td>title</td>
                        <td>string</td>
                        <td>Yes&nbsp;(either&nbsp;<span class="code">title</span>&nbsp;or&nbsp;<span class="code">oldid</span>)</td>
                        <td>The title of the page or article to make a comparison against. Namespace must be included if the page isn't in the mainspace.</td>
                    </tr>
                    <tr>
                        <td>oldid</td>
                        <td>integer</td>
                        <td>Yes (either <span class="code">title</span> or <span class="code">oldid</span>)</td>
                        <td>The revision ID (also called oldid) of the page revision to make a comparison against. If both a title and oldid are given, the oldid will be used.</td>
                    </tr>
                    <tr>
                        <td>url</td>
                        <td>string</td>
                        <td>Yes</td>
                        <td>The URL of the suspected violation source that will be compared to the page.</td>
                    </tr>
                </table>
                <table class="parameters">
                    <tr>
                        <th colspan="4"><span class="code">search</span> Mode</th>
                    </tr>
                    <tr>
                        <th>Parameter</th>
                        <th>Values</th>
                        <th>Required?</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>project</td>
                        <td>string</td>
                        <td>Yes</td>
                        <td>The project code of the site the page lives on. Examples are <span class="code">wikipedia</span> and <span class="code">wiktionary</span>. A list of acceptable values can be retrieved using <span class="code">action=sites</span>.</td>
                    </tr>
                    <tr>
                        <td>lang</td>
                        <td>string</td>
                        <td>Yes</td>
                        <td>The language code of the site the page lives on. Examples are <span class="code">en</span> and <span class="code">de</span>. A list of acceptable values can be retrieved using <span class="code">action=sites</span>.</td>
                    </tr>
                    <tr>
                        <td>title</td>
                        <td>string</td>
                        <td>Yes&nbsp;(either&nbsp;<span class="code">title</span>&nbsp;or&nbsp;<span class="code">oldid</span>)</td>
                        <td>The title of the page or article to make a check against. Namespace must be included if the page isn't in the mainspace.</td>
                    </tr>
                    <tr>
                        <td>oldid</td>
                        <td>integer</td>
                        <td>Yes (either <span class="code">title</span> or <span class="code">oldid</span>)</td>
                        <td>The revision ID (also called oldid) of the page revision to make a check against. If both a title and oldid are given, the oldid will be used.</td>
                    </tr>
                    <tr>
                        <td>use_engine</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">true</span>)</td>
                        <td>Whether to use a search engine (<a href="//developer.yahoo.com/boss/search/">Yahoo! BOSS</a>) as a source of URLs to compare against the page.</td>
                    </tr>
                    <tr>
                        <td>use_links</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">true</span>)</td>
                        <td>Whether to compare the page against external links found in its wikitext.</td>
                    </tr>
                    <tr>
                        <td>nocache</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">false</span>)</td>
                        <td>Whether to bypass search results cached from previous checks. It is recommended that you don't pass this option unless a user specifically asks for it.</td>
                    </tr>
                    <tr>
                        <td>noredirect</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">false</span>)</td>
                        <td>Whether to avoid following redirects if the given page is a redirect.</td>
                    </tr>
                    <tr>
                        <td>noskip</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">false</span>)</td>
                        <td>If a suspected source is found during a check to have a sufficiently high confidence value, the check will end prematurely, and other pending URLs will be skipped. Passing this option will prevent this behavior, resulting in complete (but more time-consuming) checks.</td>
                    </tr>
                </table>
                <h2>Responses</h2>
                <p>The JSON response object always contains a <span class="code">status</span> key, whose value is either <span class="code">ok</span> or <span class="code">error</span>. If an error has occurred, the response will look like this:</p>
<pre>{
    "status": "error",
    "error": {
        "code": (string) error code,
        "info": (string) human-readable description of error
    }
}</pre>
                <p>Valid responses for <span class="code">action=compare</span> and <span class="code">action=search</span> are formatted like this:</p>
<pre>{
    "status": "ok",
    "meta": {
        "time":       (float) time to generate results, in seconds,
        "queries":    (int) number of search engine queries made,
        "cached":     (boolean) whether or not these results are cached from an earlier search (always false in the case of action=compare),
        (only if cached=true) "cache_time": (string) human-readable time of the original search that the results are cached from
        "redirected": (boolean) whether or not a redirect was followed
    },
    "page": {
        "title": (string) the normalized title of the page checked,
        "url":   (string) the full URL of the page checked
    },
    (only if redirected=true) "original_page": {
        "title": (string) the normalized title of the original page whose redirect was followed,
        "url":   (string) the full URL of the original page whose redirect was followed
    },
    "best": {
        "url":        (string) the URL of the best match found, or null if no matches were found,
        "confidence": (float) the confidence of a violation in the best match, or 0.0 if no matches were found,
        "violation":  (string) one of "suspected", "possible", or "none"
    },
    "sources": [
        {
            "url":        (string) the URL of the source,
            "confidence": (float) the confidence of a violation in the source,
            "violation":  (string) one of "suspected", "possible", or "none",
            "skipped":    (boolean) whether or not the source was skipped due to the check finishing early (see note about noskip above)
        },
        ...
    ]
}</pre>
                <p>In the case of <span class="code">action=search</span>, <span class="code">sources</span> will contain one entry for each source checked (or skipped if the check ends early), sorted in order of confidence, with skipped sources at the bottom.</p>
                <p>In the case of <span class="code">action=compare</span>, <span class="code">best</span> will always contain information about the URL that was given, so <span class="code">response["best"]["url"]</span> will never be <span class="code">null</span>. Also, <span class="code">sources</span> will always contain one entry, with the same data as <span class="code">best</span>, since only one source is checked in comparison mode.</p>
                <p>Valid responses for <span class="code">action=sites</span> are formatted like this:</p>
<pre>{
    "status": "ok",
    "langs": [
        [
            (string) language code,
            (string) human-readable language name
        ],
        ...
    ],
    "projects": [
        [
            (string) project code,
            (string) human-readable project name
        ],
        ...
    ]
}</pre>
                <h2>Example</h2>
                <p>GET https://tools.wmflabs.org/copyvios/api.json?version=1&amp;action=search&amp;project=wikipedia&amp;lang=en&amp;title=User:The_Earwig/Sandbox/CopyvioExample</p>
<pre>
{
    "status": "ok",
    "meta": {
        "time": 2.2474379539489746,
        "queries": 1,
        "cached": false,
        "redirected": false
    },
    "page": {
        "title": "User:The Earwig/Sandbox/CopyvioExample",
        "url": "https://en.wikipedia.org/wiki/User:The_Earwig/Sandbox/CopyvioExample"
    },
    "best": {
        "url": "http://www.whitehouse.gov/administration/president-obama/",
        "confidence": 0.9886608511242603,
        "violation": "suspected"
    }
    "sources": [
        {
            "url": "http://www.whitehouse.gov/administration/president-obama/",
            "confidence": 0.9886608511242603,
            "violation": "suspected",
            "skipped": false
        },
        {
            "url": "http://maige2009.blogspot.com/2013/07/barack-h-obama-is-44th-president-of.html",
            "confidence": 0.9864798816568047,
            "violation": "suspected",
            "skipped": false
        },
        {
            "url": "http://jeuxdemonstre-apkdownload.rhcloud.com/luo-people-of-kenya-and-tanzania---wikipedia--the-free",
            "confidence": 0.0,
            "violation": "none",
            "skipped": false
        },
        {
            "url": "http://www.whitehouse.gov/about/presidents/barackobama",
            "confidence": 0.0,
            "violation": "none",
            "skipped": true
        },
        {
            "url": "http://jeuxdemonstre-apkdownload.rhcloud.com/president-barack-obama---the-white-house",
            "confidence": 0.0,
            "violation": "none",
            "skipped": true
        }
    ]
}
</pre>
            </div>
        % endif
        % if result:
            <div id="result">
                <p>You are using <span class="code">jsonfm</span> output mode, which renders JSON data as a formatted HTML document. This is intended for testing and debugging only.</p>
                ${walk_json(result)}
            </div>
        % endif
    </body>
</html>
