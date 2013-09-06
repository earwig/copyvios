<%page args="environ, cookies"/>\
<%namespace module="copyvios.background" import="get_desc_url"/>\
        </div>
        <div id="footer">
            <p>Copyright &copy; 2009&ndash;2013 <a href="//en.wikipedia.org/wiki/User:The_Earwig">Ben Kurtovic</a> &bull; \
                <a href="mailto:wikipedia.earwig@gmail.com">Contact</a> &bull; \
                <a href="https://github.com/earwig/copyvios">View Source</a> &bull; \
                % if ("CopyviosBackground" in cookies and cookies["CopyviosBackground"].value in ["potd", "list"]) or "CopyviosBackground" not in cookies:
                    <a href="${get_desc_url() | h}">Background</a> &bull; \
                % endif
                <a href="http://validator.w3.org/check?uri=referer">Valid HTML5</a>
            </p>
        </div>
    </body>
</html>
