<%include file="/support/header.mako" args="environ=environ, title='Home'"/>
            <div id="content">
            % for key, value in environ.items():
                % if key != "PATH":
                    <p><b>${key}</b>: ${value}</p>
                % endif
            % endfor
            </div>
<%include file="/support/footer.mako" args="environ=environ"/>
