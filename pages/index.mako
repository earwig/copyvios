<%include file="/support/header.mako" args="title='Index Page'"/>
% for key, value in environ.items():
            <p><b>${key}</b>: ${value}</p>
% endfor
<%include file="/support/footer.mako"/>
