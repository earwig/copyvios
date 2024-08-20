<%page args="selected_lang=None, selected_project=None"/>\
<%!
    from flask import g
    from copyvios.misc import cache
%>\
<%
    if selected_lang is None:
        if "CopyviosDefaultLang" in g.cookies:
            selected_lang = g.cookies["CopyviosDefaultLang"].value
        else:
            selected_lang = cache.bot.wiki.get_site().lang

    if selected_project is None:
        if "CopyviosDefaultProject" in g.cookies:
            selected_project = g.cookies["CopyviosDefaultProject"].value
        else:
            selected_project = cache.bot.wiki.get_site().project
%>
<div class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-dropdownInputWidget oo-ui-dropdownInputWidget-php">
    <select name="lang" required="" class="oo-ui-inputWidget-input oo-ui-indicator-down">
        % for code, name in cache.langs:
            % if code == selected_lang:
                <option value="${code | h}" selected="selected">${name}</option>
            % else:
                <option value="${code | h}">${name}</option>
            % endif
        % endfor
    </select>
</div>
<div class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-dropdownInputWidget oo-ui-dropdownInputWidget-php">
    <select name="project" required="" class="oo-ui-inputWidget-input oo-ui-indicator-down">
        % for code, name in cache.projects:
            % if code == selected_project:
                <option value="${code | h}" selected="selected">${name}</option>
            % else:
                <option value="${code | h}">${name}</option>
            % endif
        % endfor
    </select>
</div>
