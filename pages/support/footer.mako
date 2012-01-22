<%page args="environ"/>\
<%namespace name="bash" file="/bash.mako"/>\
<%!
    from os import path
%>\
<%
    root = path.dirname(environ["SCRIPT_NAME"])
    pretty = path.split(root)[0]
%>\
        </div>
        <div id="footer">
            <div id="foot-divider"></div>
            <table id="footer-box">
                <tr>
                    <td>
                        <a href="http://wiki.toolserver.org/"><img src="${root}/static/images/toolserver-button.png" title="Powered by the Wikimedia Toolserver" alt="Powered by the Wikimedia Toolserver" /></a>
                    </td>
                    <td>
                        <p>Copyright &copy; 2009&ndash;2012 <a href="http://en.wikipedia.org/wiki/User:The_Earwig">Ben Kurtovic</a> &bull; \
                            <a href="mailto:earwig@toolserver.org">Contact</a> &bull; \
                            <a href="https://github.com/earwig/toolserver">View Source</a> &bull; \
                            <a href="http://validator.w3.org/check?uri=referer">Valid XHTML 1.0 Strict</a><br />
                            <i><a class="incognito" href="${pretty}/bash">"${bash.bash()}"</a></i>
                        </p>
                    </td>
                    <td>
                        <a href="http://earwig.github.com/"><img src="${root}/static/images/earwig-button.png" title="Powered by Earwig Technology" alt="Powered by Earwig Technology" /></a>
                    </td>
                </tr>
            </table>
        </div>
    </body>
</html>