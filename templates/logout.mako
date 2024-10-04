<%!
    from json import dumps, loads
    from flask import g, request
    from copyvios.misc import cache
%>\
<%include file="/support/header.mako" args="title='Logout | Earwig\'s Copyvio Detector', splash=True"/>
<h2>Logout</h2>
<p>Logging out will prevent you from making search engine checks.</p>
<form action="${request.script_root}/logout" method="post">
    <div class="oo-ui-layout oo-ui-fieldLayout oo-ui-fieldLayout-align-left">
        <div class="oo-ui-fieldLayout-body">
            <span class="oo-ui-fieldLayout-field">
                <span class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-labelElement oo-ui-buttonInputWidget">
                    <button type="submit" class="oo-ui-inputWidget-input oo-ui-buttonElement-button">
                        <span class="oo-ui-labelElement-label">Logout</span>
                    </button>
                </span>
            </span>
        </div>
    </div>
</form>
<%include file="/support/footer.mako"/>
