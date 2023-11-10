<%!
    from json import dumps
    from flask import url_for
%>\
<%def name="do_indent(size)">
    <br />
    % for i in xrange(size):
        <div class="indent"></div>
    % endfor
</%def>\
<%def name="walk_json(obj, indent=0)">
    % if isinstance(obj, type({})):
        {
        % for key in obj:
            ${do_indent(indent + 1)}
            "${key | h}": ${walk_json(obj[key], indent + 1)}${"," if not loop.last else ""}
        % endfor
        ${do_indent(indent)}
        }
    % elif isinstance(obj, (list, tuple, set)):
        [
        % for elem in obj:
            ${do_indent(indent + 1)}
            ${walk_json(elem, indent + 1)}${"," if not loop.last else ""}
        % endfor
        ${do_indent(indent)}
        ]
    % else:
        ${dumps(obj) | h}
    % endif
</%def>\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>API &ndash; Earwig's Copyvio Detector</title>
        <link rel="stylesheet" href="${request.script_root}${url_for('static', file='api.min.css')}" type="text/css" />
    </head>
    <body>
        % if help:
            <div id="help">
                <h1>Copyvio Detector API</h1>
                <p>This is the first version of the <a href="https://en.wikipedia.org/wiki/Application_programming_interface">API</a> for <a href="${request.script_root}/">Earwig's Copyvio Detector</a>. Please <a href="https://github.com/earwig/copyvios/issues">report any issues</a> you encounter.</p>
                <h2>Requests</h2>
                <p>The API responds to GET requests made to <span class="code">https://copyvios.toolforge.org/api.json</span>. Parameters are described in the tables below:</p>
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
                        <td>The default output format is <a href="https://www.json.org/">JSON</a>. <span class="code">jsonfm</span> mode produces the same output, but renders it as a formatted HTML document for debugging.</td>
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
                    <tr>
                        <td>detail</td>
                        <td>boolean</td>
                        <td>No (default: <span class="code">false</span>)</td>
                        <td>Whether to include the detailed HTML text comparison available in the regular interface. If not, only the similarity percentage is available.</td>
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
                        <td>Whether to use a search engine (<a href="https://developers.google.com/custom-search/">Google</a>) as a source of URLs to compare against the page.</td>
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
                        <td>If a suspected source is found during a check to have a sufficiently high similarity value, the check will end prematurely, and other pending URLs will be skipped. Passing this option will prevent this behavior, resulting in complete (but more time-consuming) checks.</td>
                    </tr>
                </table>
                <h2>Responses</h2>
                <p>The JSON response object always contains a <span class="code">status</span> key, whose value is either <span class="code">ok</span> or <span class="code">error</span>. If an error has occurred, the response will look like this:</p>
                <pre>{
    "status": "error",
    "error": {
        "code": <span class="resp-dtype">string</span> <span class="resp-desc">error code</span>,
        "info": <span class="resp-dtype">string</span> <span class="resp-desc">human-readable description of error</span>
    }
}</pre>
                <p>Valid responses for <span class="code">action=compare</span> and <span class="code">action=search</span> are formatted like this:</p>
                <pre>{
    "status": "ok",
    "meta": {
        "time":       <span class="resp-dtype">float</span> <span class="resp-desc">time to generate results, in seconds</span>,
        "queries":    <span class="resp-dtype">int</span> <span class="resp-desc">number of search engine queries made</span>,
        "cached":     <span class="resp-dtype">boolean</span> <span class="resp-desc">whether these results are cached from an earlier search (always false in the case of action=compare)</span>,
        "redirected": <span class="resp-dtype">boolean</span> <span class="resp-desc">whether a redirect was followed</span>,
        <span class="resp-cond">only if cached=true</span> "cache_time": <span class="resp-dtype">string</span> <span class="resp-desc">human-readable time of the original search that the results are cached from</span>
    },
    "page": {
        "title": <span class="resp-dtype">string</span> <span class="resp-desc">the normalized title of the page checked</span>,
        "url":   <span class="resp-dtype">string</span> <span class="resp-desc">the full URL of the page checked</span>
    },
    <span class="resp-cond">only if redirected=true</span> "original_page": {
        "title": <span class="resp-dtype">string</span> <span class="resp-desc">the normalized title of the original page whose redirect was followed</span>,
        "url":   <span class="resp-dtype">string</span> <span class="resp-desc">the full URL of the original page whose redirect was followed</span>
    },
    "best": {
        "url":        <span class="resp-dtype">string</span> <span class="resp-desc">the URL of the best match found, or null if no matches were found</span>,
        "confidence": <span class="resp-dtype">float</span> <span class="resp-desc">the similarity of a violation in the best match, or 0.0 if no matches were found</span>,
        "violation":  <span class="resp-dtype">string</span> <span class="resp-desc">one of "suspected", "possible", or "none"</span>
    },
    "sources": [
        {
            "url":        <span class="resp-dtype">string</span> <span class="resp-desc">the URL of the source</span>,
            "confidence": <span class="resp-dtype">float</span> <span class="resp-desc">the similarity of the source to the page checked as a ratio between 0.0 and 1.0</span>,
            "violation":  <span class="resp-dtype">string</span> <span class="resp-desc">one of "suspected", "possible", or "none"</span>,
            "skipped":    <span class="resp-dtype">boolean</span> <span class="resp-desc">whether the source was skipped due to the check finishing early (see note about noskip above) or an exclusion</span>,
            "excluded":    <span class="resp-dtype">boolean</span> <span class="resp-desc">whether the source was skipped for being in the excluded URL list</span>
        },
        ...
    ],
    <span class="resp-cond">only if action=compare and detail=true</span> "detail": {
        "article": <span class="resp-dtype">string</span> <span class="resp-desc">article text, with shared passages marked with HTML</span>,
        "source":  <span class="resp-dtype">string</span> <span class="resp-desc">source text, with shared passages marked with HTML</span>
    }
}</pre>
                <p>In the case of <span class="code">action=search</span>, <span class="code">sources</span> will contain one entry for each source checked (or skipped if the check ends early), sorted by similarity, with skipped and excluded sources at the bottom.</p>
                <p>In the case of <span class="code">action=compare</span>, <span class="code">best</span> will always contain information about the URL that was given, so <span class="code">response["best"]["url"]</span> will never be <span class="code">null</span>. Also, <span class="code">sources</span> will always contain one entry, with the same data as <span class="code">best</span>, since only one source is checked in comparison mode.</p>
                <p>Valid responses for <span class="code">action=sites</span> are formatted like this:</p>
                <pre>{
    "status": "ok",
    "langs": [
        [
            <span class="resp-dtype">string</span> <span class="resp-desc">language code</span>,
            <span class="resp-dtype">string</span> <span class="resp-desc">human-readable language name</span>
        ],
        ...
    ],
    "projects": [
        [
            <span class="resp-dtype">string</span> <span class="resp-desc">project code</span>,
            <span class="resp-dtype">string</span> <span class="resp-desc">human-readable project name</span>
        ],
        ...
    ]
}</pre>
                <h2>Etiquette</h2>
                <p>The tool uses the same workers to handle all requests, so making concurrent API calls is only going to slow you down. Most operations are not rate-limited, but full searches with <span class="code">use_engine=True</span> are globally limited to around a thousand per day. Be respectful!</p>
                <p>Aside from testing, you must set a reasonable <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent">user agent</a> that identifies your bot and and gives some way to contact you. You may be blocked if using an improper user agent (for example, the default user agent set by your HTTP library), or if your bot makes requests too frequently.</p>
                <h2>Example</h2>
                <p><a class="no-color" href="https://copyvios.toolforge.org/api.json?version=1&amp;action=search&amp;project=wikipedia&amp;lang=en&amp;title=User:EarwigBot/Copyvios/Tests/2"><span class="code">https://copyvios.toolforge.org/api.json?<span class="param-key">version</span>=<span class="param-val">1</span>&amp;<span class="param-key">action</span>=<span class="param-val">search</span>&amp;<span class="param-key">project</span>=<span class="param-val">wikipedia</span>&amp;<span class="param-key">lang</span>=<span class="param-val">en</span>&amp;<span class="param-key">title</span>=<span class="param-val">User:EarwigBot/Copyvios/Tests/2</span></span></a></p>
                <pre>{
    "status": "ok",
    "meta": {
        "time": 2.2474379539489746,
        "queries": 1,
        "cached": false,
        "redirected": false
    },
    "page": {
        "title": "User:EarwigBot/Copyvios/Tests/2",
        "url": "https://en.wikipedia.org/wiki/User:EarwigBot/Copyvios/Tests/2"
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
            "skipped": false,
            "excluded": false
        },
        {
            "url": "http://maige2009.blogspot.com/2013/07/barack-h-obama-is-44th-president-of.html",
            "confidence": 0.9864798816568047,
            "violation": "suspected",
            "skipped": false,
            "excluded": false
        },
        {
            "url": "http://jeuxdemonstre-apkdownload.rhcloud.com/luo-people-of-kenya-and-tanzania---wikipedia--the-free",
            "confidence": 0.0,
            "violation": "none",
            "skipped": false,
            "excluded": false
        },
        {
            "url": "http://www.whitehouse.gov/about/presidents/barackobama",
            "confidence": 0.0,
            "violation": "none",
            "skipped": true,
            "excluded": false
        },
        {
            "url": "http://jeuxdemonstre-apkdownload.rhcloud.com/president-barack-obama---the-white-house",
            "confidence": 0.0,
            "violation": "none",
            "skipped": true,
            "excluded": false
        }
    ]
}
</pre>
            </div>
        % endif
        % if result:
            <div id="result">
                <p>You are using <span class="code">jsonfm</span> output mode, which renders JSON data as a formatted HTML document. This is intended for testing and debugging only.</p>
                <div class="json">
                    ${walk_json(result)}
                </div>
            </div>
        % endif
    </body>
</html>
