<%! from flask import g, request %>\
        </div>
        <div id="footer">
            <p>Copyright &copy; 2009&ndash;2014 <a href="//en.wikipedia.org/wiki/User:The_Earwig">Ben Kurtovic</a> &bull; \
                <a href="${request.script_root}/api.json">API</a> &bull; \
                <a href="https://github.com/earwig/copyvios">Source Code</a> &bull; \
                % if ("CopyviosBackground" in g.cookies and g.cookies["CopyviosBackground"].value in ["potd", "list"]) or "CopyviosBackground" not in g.cookies:
                    <a href="${g.descurl | h}">Background</a> &bull; \
                % endif
                <a href="http://validator.w3.org/check?uri=referer">Valid HTML5</a>
            </p>
        </div>
    </body>
</html>
