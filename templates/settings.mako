<%!
    from json import dumps, loads
    from flask import request
    from copyvios.cookies import get_cookies
    from copyvios.cache import cache
%>\
<%
    cookies = get_cookies()
%>\
<%include file="/support/header.mako" args="title='Settings | Earwig\'s Copyvio Detector', splash=True"/>
% if status:
    <div id="info-box" class="green-box">
        <p>${status}</p>
    </div>
% endif
<h2>Settings</h2>
<p>This page contains some configurable options for the copyvio detector. Settings are saved as cookies.</p>
<form action="${request.script_root}/settings" method="post">
    <h3>Default site</h2>
    <div class="oo-ui-layout oo-ui-labelElement oo-ui-fieldLayout oo-ui-fieldLayout-align-top">
        <div class="oo-ui-fieldLayout-body">
            <div class="oo-ui-fieldLayout-field">
                <div class="oo-ui-widget oo-ui-widget-enabled">
                    <div class="oo-ui-layout oo-ui-horizontalLayout">
                        <div class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-dropdownInputWidget oo-ui-dropdownInputWidget-php">
                            <select name="lang" required="" class="oo-ui-inputWidget-input oo-ui-indicator-down">
                                <% selected_lang = cookies["CopyviosDefaultLang"].value if "CopyviosDefaultLang" in cookies else default_lang %>\
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
                                <% selected_project = cookies["CopyviosDefaultProject"].value if "CopyviosDefaultProject" in cookies else default_project %>\
                                % for code, name in cache.projects:
                                    % if code == selected_project:
                                        <option value="${code | h}" selected="selected">${name}</option>
                                    % else:
                                        <option value="${code | h}">${name}</option>
                                    % endif
                                % endfor
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <h3>Background</h2>
    <%
        background_options = [
            ("list", 'Randomly select from <a href="https://commons.wikimedia.org/wiki/User:The_Earwig/POTD">a subset</a> of previous <a href="https://commons.wikimedia.org/">Wikimedia Commons</a> <a href="https://commons.wikimedia.org/wiki/Commons:Picture_of_the_day">Pictures of the Day</a> that work well as widescreen backgrounds, refreshed daily (default).'),
            ("potd", 'Use the current Commons Picture of the Day, unfiltered. Certain POTDs may be unsuitable as backgrounds due to their aspect ratio or subject matter.'),
            ("plain", "Use a plain background."),
        ]
        selected = cookies["CopyviosBackground"].value if "CopyviosBackground" in cookies else "list"
    %>\
    <div class="oo-ui-layout oo-ui-labelElement oo-ui-fieldLayout oo-ui-fieldLayout-align-top">
        <div class="oo-ui-fieldLayout-body">
            <div class="oo-ui-fieldLayout-field">
                <div class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-radioSelectInputWidget">
                    % for value, desc in background_options:
                        <div class="oo-ui-layout oo-ui-labelElement oo-ui-fieldLayout oo-ui-fieldLayout-align-inline">
                            <div class="oo-ui-fieldLayout-body">
                                <span class="oo-ui-fieldLayout-field">
                                    <span class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-radioInputWidget">
                                        <input id="background-${value}" class="oo-ui-inputWidget-input" type="radio" name="background" value="${value}" ${'checked="checked"' if value == selected else ''}><span></span>
                                    </span>
                                </span>
                                <span class="oo-ui-fieldLayout-header">
                                    <label for="background-${value}" class="oo-ui-labelElement-label">${desc}</label>
                                </span>
                            </div>
                        </div>
                    % endfor
                </div>
            </div>
        </div>
    </div>

    <input type="hidden" name="action" value="set"/>
    <div class="oo-ui-layout oo-ui-fieldLayout oo-ui-fieldLayout-align-left">
        <div class="oo-ui-fieldLayout-body">
            <span class="oo-ui-fieldLayout-field">
                <span class="oo-ui-widget oo-ui-widget-enabled oo-ui-inputWidget oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-labelElement oo-ui-buttonInputWidget">
                    <button type="submit" class="oo-ui-inputWidget-input oo-ui-buttonElement-button">
                        <span class="oo-ui-labelElement-label">Save</span>
                    </button>
                </span>
            </span>
        </div>
    </div>
</form>
<%include file="/support/footer.mako"/>
