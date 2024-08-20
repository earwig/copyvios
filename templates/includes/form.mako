<%!
    from flask import g, request
    from copyvios.misc import cache
%>
<%namespace name="ooui" file="/includes/ooui.mako"/>
<form id="cv-form" action="${request.script_root}/" method="get">
    <%ooui:horizontal_layout>
        <label class="site oo-ui-widget oo-ui-widget-enabled oo-ui-labelElement-label oo-ui-labelElement oo-ui-labelWidget">Site</label>
        <%include file="/includes/site.mako" args="selected_lang=query.orig_lang, selected_project=query.project"/>
    </%ooui:horizontal_layout>
    <%ooui:horizontal_layout>
        <label for="cv-title" class="page oo-ui-widget oo-ui-widget-enabled oo-ui-labelElement-label oo-ui-labelElement oo-ui-labelWidget">Page</label>
        <%ooui:text classes="page-title">
            <input id="cv-title" type="text" class="oo-ui-inputWidget-input" name="title" placeholder="Title" title="Page title"
                % if query.title:
                    value="${query.page.title if query.page else query.title | h}"
                % endif
            >
        </%ooui:text>
        <label class="oo-ui-widget oo-ui-widget-enabled oo-ui-labelElement-label oo-ui-labelElement oo-ui-labelWidget">or</label>
        <%ooui:text classes="page-oldid">
            <input id="cv-oldid" type="text" class="oo-ui-inputWidget-input" name="oldid" placeholder="Revision ID" title="Revision ID"
                % if query.oldid:
                    value="${query.oldid | h}"
                % endif
            >
        </%ooui:text>
    </%ooui:horizontal_layout>

    <%ooui:menu_layout>
        <%ooui:menu_layout_menu>
            ${ooui.menu_layout_tab('search', 'Copyvio search', selected=query.action == "search" or not query.action)}
            ${ooui.menu_layout_tab('compare', 'Copyvio compare', selected=query.action == "compare")}
        </%ooui:menu_layout_menu>
        <%ooui:menu_layout_content>
            <%ooui:menu_layout_panel name="search" active="${query.action == 'search' or not query.action}">
                Search!
            </%ooui:menu_layout_panel>
            <%ooui:menu_layout_panel name="compare" active="${query.action == 'compare'}">
                Compare!
            </%ooui:menu_layout_panel>
        </%ooui:menu_layout_content>
    </%ooui:menu_layout>
</form>
