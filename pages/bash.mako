<%!
    from random import choice
    bashes = [
        "Now 20% cooler!",
        "I make tools and tool accessories."
    ]
%>\
<%def name="bash()">${choice(bashes)}</%def>\
<%include file="/support/header.mako" args="environ=environ, title='Home'"/>
            <div id="content">
                <ul>
                    % for bash in bashes:
                        <li>${bash}</li>
                    % endfor
                </ul>
            </div>
<%include file="/support/footer.mako" args="environ=environ"/>
