<%!
    from datetime import datetime
    from flask import g, request
%>\
            </main>
        </div>
        <div class="padding"></div>
    </div>
    <footer>
        <ul>
            <li>Maintained by <a href="https://en.wikipedia.org/wiki/User:The_Earwig">Ben Kurtovic</a></li>
            <li><a href="${request.script_root}/api">API</a></li>
            <li><a href="https://github.com/earwig/copyvios">Source code</a></li>
            % if ("CopyviosBackground" in g.cookies and g.cookies["CopyviosBackground"].value in ["potd", "list"]) or "CopyviosBackground" not in g.cookies:
                <li><a href="${g.descurl | h}">Background image</a></li>
            % endif
        </ul>
    </footer>
</body>
</html>
