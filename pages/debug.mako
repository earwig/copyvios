<%include file="/support/header.mako" args="environ=environ, title='Debug'"/>
        <ul>
        % for key, value in environ.items():
            % if key not in ["wsgi.input", "wsgi.errors", "PATH"]:
                <li><b>${key}</b>: ${value | h}</li>
            % elif key == "wsgi.input":
                <li><b>${key}</b>: ${value.read(environ.get("CONTENT_LENGTH", 0)) | h}</li>
            % endif
        % endfor
        </ul>
<%include file="/support/footer.mako" args="environ=environ"/>
