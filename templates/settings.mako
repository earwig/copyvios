<%!
    from json import dumps, loads
    from flask import g, request
    from copyvios.misc import cache
%>\
<%include file="/includes/header.mako" args="title='Settings - Earwig\'s Copyvio Detector', splash=True"/>
<%namespace name="ooui" file="/includes/ooui.mako"/>
% if status:
    <div id="info-box" class="green-box">
        <p>${status}</p>
    </div>
% endif
<h2>Settings</h2>
<p>This page contains some configurable options for the copyvio detector. Settings are saved as cookies.</p>
<form action="${request.script_root}/settings" method="post">
    <h3>Default site</h3>
    <%ooui:field_layout>
        <%ooui:widget>
            <%ooui:horizontal_layout>
                <%include file="/includes/site.mako"/>
            </%ooui:horizontal_layout>
        </%ooui:widget>
    </%ooui:field_layout>

    <h3>Background</h3>
    <%
        background_options = [
            ("list", 'Randomly select from <a href="https://commons.wikimedia.org/wiki/User:The_Earwig/POTD">a subset</a> of previous <a href="https://commons.wikimedia.org/">Wikimedia Commons</a> <a href="https://commons.wikimedia.org/wiki/Commons:Picture_of_the_day">Pictures of the Day</a> that work well as widescreen backgrounds, refreshed daily (default).'),
            ("potd", 'Use the current Commons Picture of the Day, unfiltered. Certain POTDs may be unsuitable as backgrounds due to their aspect ratio or subject matter.'),
            ("plain", "Use a plain background."),
        ]
        selected = g.cookies["CopyviosBackground"].value if "CopyviosBackground" in g.cookies else "list"
    %>
    <%ooui:field_layout>
        <%ooui:radio_select>
            % for value, desc in background_options:
                <%ooui:field_layout align="inline">
                    <%ooui:radio>
                        <input id="background-${value}" class="oo-ui-inputWidget-input" type="radio" name="background" value="${value}" ${'checked="checked"' if value == selected else ''}><span></span>
                    </%ooui:radio>
                    <%ooui:field_layout_header>
                        <label for="background-${value}" class="oo-ui-labelElement-label">${desc}</label>
                    </%ooui:field_layout_header>
                </%ooui:field_layout>
            % endfor
        </%ooui:radio_select>
    </%ooui:field_layout>

    <h3>Highlight colors</h3>
    <p><em>This is not currently configurable, but it will be soon.</em></p>
    <div>
        Default:
        % for i in range(1, 9):
            <span class="highlight-demo cv-hl cv-hl-${i}">${i}</span>
        % endfor
        <span class="highlight-demo cv-hl">9+</span>
    </div>

    <input type="hidden" name="action" value="set"/>
    <%ooui:field_layout align="left">
        ${ooui.submit_button(label="Save")}
    </%ooui:field_layout>
</form>
<%include file="/includes/footer.mako"/>
