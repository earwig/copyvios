<%include file="/support/header.mako" args="title='Debug - Earwig\'s Copyvio Detector'"/>
<%! from flask import request %>\
<ul>
% for key, value in request.environ.items():
    % if key not in ["wsgi.input", "wsgi.errors", "PATH"]:
        <li><b>${key}</b>: ${value | h}</li>
    % endif
% endfor
</ul>
<%include file="/support/footer.mako"/>
