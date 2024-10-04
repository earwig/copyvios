<%!
    from json import dumps, loads
    from flask import g, request
    from copyvios.misc import cache
    from urlparse import parse_qsl
%>\
<%include file="/support/header.mako" args="title='Login | Earwig\'s Copyvio Detector', splash=True"/>
% if error:
    <div id="info-box" class="red-box">
        <p>Error trying to log in: ${error | h}</p>
    </div>
% endif
<h2>Login</h2>
<p>You are required to log in with your Wikimedia account to perform checks with the search engine.</p>
%if request.args.get('next'):
    <p>
        After logging in,
        % if request.args["next"][0:2] == "/?" and dict(parse_qsl(request.args["next"])).get("action") == "search":
            your check will be run.
        % else:
            you will be redirected to: ${request.args.get('next') | h}
        % endif
    </p>
%endif
<form action="${request.script_root}/login" method="post">
    <input type="hidden" name="next" value="${request.args.get('next', '/') | h}" />
    <div class="oo-ui-layout oo-ui-fieldLayout oo-ui-fieldLayout-align-left">
        <div class="oo-ui-fieldLayout-body">
            <span class="oo-ui-fieldLayout-field">
                <span class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-labelElement oo-ui-buttonInputWidget">
                    <button type="submit" class="oo-ui-inputWidget-input oo-ui-buttonElement-button">
                        <span class="oo-ui-labelElement-label">Login</span>
                    </button>
                </span>
            </span>
        </div>
    </div>
</form>
<%include file="/support/footer.mako"/>
