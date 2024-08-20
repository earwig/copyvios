<%def name="widget(classes='', raw_classes='')">
    <div class="oo-ui-widget oo-ui-widget-enabled ${' '.join('oo-ui-%s' % cls for cls in classes.strip().split())} ${' '.join(raw_classes.strip().split())}">
        ${caller.body()}
    </div>
</%def>

<%def name="field_layout(align='top')">
    <div class="oo-ui-layout oo-ui-fieldLayout oo-ui-fieldLayout-align-${align} oo-ui-labelElement">
        <div class="oo-ui-fieldLayout-body">
            <div class="oo-ui-fieldLayout-field">
                ${caller.body()}
            </div>
        </div>
    </div>
</%def>

<%def name="field_layout_header()">
    </div>
    <div class="oo-ui-fieldLayout-header">
        ${caller.body()}
</%def>

<%def name="horizontal_layout()">
    <div class="oo-ui-layout oo-ui-horizontalLayout">
        ${caller.body()}
    </div>
</%def>

<%def name="menu_layout()">
    <div class="oo-ui-layout oo-ui-menuLayout oo-ui-menuLayout-static oo-ui-menuLayout-top oo-ui-menuLayout-showMenu oo-ui-indexLayout">
        ${caller.body()}
    </div>
</%def>

<%def name="menu_layout_menu(frame_style='frameless')">
    <div class="oo-ui-menuLayout-menu">
        <div class="oo-ui-layout oo-ui-panelLayout oo-ui-indexLayout-tabPanel">
            <div role="tablist" tabindex="0" class="oo-ui-selectWidget oo-ui-selectWidget-unpressed oo-ui-widget oo-ui-widget-enabled oo-ui-tabSelectWidget oo-ui-tabSelectWidget-${frame_style}">
                ${caller.body()}
            </div>
        </div>
    </div>
</%def>

<%def name="menu_layout_tab(name, label, selected=False)">
    <div aria-selected="${'true' if selected else 'false'}" role="tab" class="oo-ui-widget oo-ui-widget-enabled oo-ui-optionWidget oo-ui-tabOptionWidget oo-ui-labelElement${' oo-ui-optionWidget-selected' if selected else ''}" data-name="${name}">
        <span class="oo-ui-labelElement-label">${label}</span>
    </div>
</%def>

<%def name="menu_layout_content()">
    <div class="oo-ui-menuLayout-content">
        <div class="oo-ui-layout oo-ui-panelLayout oo-ui-stackLayout oo-ui-indexLayout-stackLayout">
            ${caller.body()}
        </div>
    </div>
</%def>

<%def name="menu_layout_panel(name, active='false')">
    <div role="tabpanel"${'' if active else ' aria-hidden="true"'} class="oo-ui-layout oo-ui-panelLayout oo-ui-panelLayout-scrollable oo-ui-tabPanelLayout ${'oo-ui-tabPanelLayout-active' if active else 'oo-ui-element-hidden'}" data-name="${name}">
        ${caller.body()}
    </div>
</%def>

<%def name="radio_select()">
    <%self:widget classes="inputWidget radioSelectInputWidget">
        ${caller.body()}
    </%self:widget>
</%def>

<%def name="radio()">
    <%self:widget classes="inputWidget radioInputWidget">
        ${caller.body()}
    </%self:widget>
</%def>

<%def name="text(classes='')">
    <%self:widget classes="inputWidget textInputWidget textInputWidget-type-text textInputWidget-php" raw_classes="${classes}">
        ${caller.body()}
    </%self:widget>
</%def>

<%def name="submit_button(label)">
    <%self:widget classes="inputWidget buttonElement buttonElement-framed labelElement flaggedElement-primary flaggedElement-progressive buttonInputWidget">
        <button type="submit" class="oo-ui-inputWidget-input oo-ui-buttonElement-button">
            <span class="oo-ui-labelElement-label">${label}</span>
        </button>
    </%self:widget>
</%def>
