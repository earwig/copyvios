<%!
    from sys import path
    from urlparse import parse_qs

    path.insert(0, "../earwigbot")

    import earwigbot
%>\
<%
    query = parse_qs(environ["QUERY_STRING"])
    try:
        lang = query["lang"][0]
        project = query["project"][0]
        title = query["title"][0]
    except (KeyError, IndexError):
        page = None
    else:
        earwigbot.config.config.load("config.ts-earwigbot.json")
        try:
            site = earwigbot.wiki.get_site(lang=lang, project=project)
        except earwigbot.wiki.SiteNotFoundError:
            page = None
        else:
            page = site.get_page(title)
%>\
<%include file="/support/header.mako" args="environ=environ, title='Copyvio Detector'"/>
            <h1>Copyvio Detector</h1>
            <p>This tool attempts to detect <a href="http://en.wikipedia.org/wiki/WP:COPYVIO">copyright violations</a> in Wikipedia articles.</p>
            <form action="${environ['PATH_INFO']}" method="get">
                <table>
                    <tr>
                        <td>Site:</td>
                        <td>
                            <select name="lang">
                                <option value="en" selected="selected">en (English)</option>
                            </select>
                            <select name="project">
                                <option value="wikipedia" selected="selected">Wikipedia</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <td>Page title:</td>
                        % if page:
                            <td><input type="text" name="title" size="50" value="${page.title()}" /></td>
                        % else:
                            <td><input type="text" name="title" size="50" /></td>
                        % endif
                    </tr>
                    <tr>
                        <td><button type="submit">Submit</button></td>
                    </tr>
                </table>
            </form>
            % if page:
                <fieldset id="result">
                    <legend>Result for <a href="${page.url()}">${page.title()}</a>:</legend>
                    <p>Watch this space!</p>
                </fieldset>
            % endif
<%include file="/support/footer.mako" args="environ=environ"/>
