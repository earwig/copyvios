<%!
    from random import choice
    bashes = [
        "Now 20% cooler!",
        "I make tools and tool accessories."
    ]
%>\
<%def name="bash()">${choice(bashes)}</%def>\
<%include file="/support/header.mako" args="environ=environ, title='Bash'"/>
            <ol>
            % for bash in bashes:
                <li>${bash}</li>
            % endfor
            </ol>
<%include file="/support/footer.mako" args="environ=environ"/>
