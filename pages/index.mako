<%include file="/support/header.mako" args="title='Index Page'"/>
            <div id="content">
% for key, value in environ.items():
                <p><b>${key}</b>: ${value}</p>
% endfor
            </div>
<%include file="/support/footer.mako"/>
