function updateScreenSize() {
    var cache = cacheCookie();
    var data = {
        "width": window.screen.availWidth,
        "height": window.screen.availHeight
    }
    if (!cache || cache["width"] != data["width"] || cache["height"] != data["height"]) {
        setCookie("CopyviosScreenCache", JSON.stringify(data), 1095);
    }
}

function cacheCookie() {
    var cookie = getCookie("CopyviosScreenCache");
    if (cookie) {
        try {
            data = JSON.parse(cookie);
            var width = data.width;
            var height = data.height;
            if (width && height) {
                return {"width": width, "height": height};
            }
        }
        catch (SyntaxError) {}
    }
    return false;
}

// Cookie code partially based on http://www.quirksmode.org/js/cookies.html

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(";");
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == " ") {
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) == 0) {
            var value = window.atob(c.substring(nameEQ.length, c.length));
            if (value.indexOf("--cpv2") == 0) {
                return value.substring("--cpv2".length, value.length);
            }
        }
    }
    return null;
}

function setCookieWithDate(name, value, date) {
    value = window.btoa("--cpv2" + value);
    if (date) {
        var expires = ";expires=" + date.toUTCString();
    }
    else {
        var expires = "";
    }
    document.cookie = name + "=" + value + expires + ";path=/;samesite=lax";
}

function setCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        setCookieWithDate(name, value, date);
    }
    else {
        setCookieWithDate(name, value);
    }
}

function selectTab(e) {
    var tab = $(e.target);
    if (tab.hasClass("oo-ui-optionWidget-selected")) {
        return false;
    }
    var name = tab.data("name");
    var menu = tab.closest(".oo-ui-menuLayout");
    menu.find(".oo-ui-optionWidget-selected")
        .removeClass("oo-ui-optionWidget-selected")
        .attr("aria-selected", "false");
    tab.addClass("oo-ui-optionWidget-selected")
        .attr("aria-selected", "true");
    menu.find(".oo-ui-tabPanelLayout-active")
        .removeClass("oo-ui-tabPanelLayout-active")
        .addClass("oo-ui-element-hidden")
        .attr("aria-hidden", "true");
    menu.find('.oo-ui-tabPanelLayout[data-name="' + name + '"]')
        .addClass("oo-ui-tabPanelLayout-active")
        .removeClass("oo-ui-element-hidden")
        .removeAttr("aria-hidden");
    return false;
}

function submitForm() {
    $("#cv-form button[type='submit']")
        .prop("disabled", true)
        .css("cursor", "progress")
        .parent()
        .addClass("oo-ui-widget-disabled")
        .removeClass("oo-ui-widget-enabled");
}

function toggleNotice() {
    var details = $("#notice-collapse-box"),
        trigger = $("#notice-collapse-trigger");
    if (details.is(":hidden")) {
        details.show();
        trigger.text("[hide]");
    }
    else {
        details.hide();
        trigger.text("[show]");
    }
}

function setNotice() {
    var details = $("#notice-collapse-box"),
        trigger = $("#notice-collapse-trigger");
    if (details.length >= 0 && trigger.length >= 0) {
        trigger.replaceWith($("<a>", {
            id: "notice-collapse-trigger",
            href: "#",
            text: "[show]",
            click: function() {
                toggleNotice();
                return false;
            }
        }));
        details.hide();
    }
}

function addUrl() {
    var template = $("#compare-new-url");
    var widget = template[0].content.cloneNode(true);
    $(widget).find("input").prop("name", "url" + ($(".compare-url").length + 1));
    $(widget).find(".compare-remove-url").click(removeUrl);
    template.before(widget);
    return false;
}

function removeUrl(e) {
    $(e.target).closest(".oo-ui-layout").remove();
    $(".compare-url:not(.compare-url-first)").each(function(i, e) {
        $(e).find("input").prop("name", "url" + (i + 2));
    });
    return false;
}

function pasteText() {
    // TODO
    return false;
}

function uploadFile() {
    // TODO
    return false;
}

function selectResult(n) {
    var select = $(".cv-chain-source-" + n);
    if (select.length === 0) {
        return;
    }
    $(".cv-chain-source").addClass("hidden");
    select.removeClass("hidden");
    $(".source-row-selected").removeClass("source-row-selected");
    $($(".source-row")[n - 1]).addClass("source-row-selected");
    $(".source-tooltip > .tooltip-align-right").remove();
    $(".source-tooltip-selected").removeClass("source-tooltip-selected");
    $(".source-tooltip").filter(function(i, elem) {
        return elem.dataset.id === n.toString();
    }).addClass("source-tooltip-selected");
}

function setResultSelectionHandlers() {
    $(".source-compare").click(function(e) {
        selectResult($(e.target).data("id"));
        return false;
    });

    $("#cv-result-sources tr:not(:first-child)").click(function(e) {
        if (e.target.tagName === "TD") {
            selectResult($(e.target).parent().data("id"));
            return false;
        }
    });
}

function toggleSource(e) {
    var el = $(e.target),
        id = el.data("id");
    if (el.hasClass("cv-hl")) {
        $(".cv-hl-" + id)
            .addClass("cv-hl-disabled-" + id)
            .removeClass(["cv-hl-" + id, "cv-hl"]);
    } else {
        $(".cv-hl-disabled-" + id)
            .addClass(["cv-hl-" + id, "cv-hl"])
            .removeClass("cv-hl-disabled-" + id);
    }
    return false;
}

function unselectRegions() {
    if ($(".source-tooltip, .cv-selected").length > 0) {
        $(".source-tooltip").remove();
        $(".cv-selected").removeClass("cv-selected");
        return false;
    }
}

function selectRegion(e) {
    unselectRegions();
    var target = $(e.target).closest(".cv-hl");
    if (target.length === 0) {
        return;
    }
    var hls = [].slice.apply(target[0].classList).filter(function(c) {
        return c.startsWith("cv-hl-");
    });
    if (hls.length === 0) {
        return;
    }
    var num = parseInt(hls[0].substr(6));
    var url = null, selected = true;
    if ($("#cv-result-sources").length > 0) {
        url = $(".source-url-" + num);
        if (url.length === 0) {
            return;
        }
        selected = $(".source-row-selected").data("id") === num;
    }
    var wordcount = target.text().split(/\s+/).filter(function(s) { return s != '' }).length;
    var width;

    var contents = $("<span>");
    if (url !== null) {
        var domain = url.data("domain") || url.text();
        contents.append(
            $("<a>", {
                class: "selector",
                href: "#",
                title: "Select source",
            })
            .text("Source " + num)
            .click(function() {
                selectResult(num);
                return false;
            })
        ).append(
            $("<strong>", {class: "selector"})
            .text("Source " + num)
        ).append(" ")
        .append(
            $("<span>", {class: "domain"})
            .text("(" + domain + "):")
        ).append(" ");
        width = Math.min(15 + domain.length / 2, 30);
    } else {
        width = 8;
    }
    contents
        .append(
            $("<span>", {class: "wordcount"})
            .text(wordcount.toString() + " words")
        ).click(function() {
            if ($(".source-row-selected").data("id") === num) {
                unselectRegions();
            } else {
                selectResult(num);
            }
            return false;
        });

    var container = $("#source-tooltips");
    var containerOffset = container.offset();
    var chain = target.closest(".cv-chain-cell");
    var tooltipDirection = chain.hasClass("cv-chain-source") ? "right" : "left";
    var tooltip = $("<div>", {class: "source-tooltip tooltip-anchor-fixed"})
        .css({
            top: (e.pageY - containerOffset.top) + "px",
            left: (e.pageX - containerOffset.left) + "px",
        })
        .append(
            $("<span>", {class: "tooltip tooltip-align-" + tooltipDirection})
            .css({
                width: width + "em",
            }).append(contents)
        ).appendTo(container)
        .attr("data-id", num.toString());
    if (selected) {
        tooltip.addClass("source-tooltip-selected");
    }
    target.addClass("cv-selected");
    return false;
}

function hideAdditionalSources() {
    if ($("#cv-additional").length >= 0) {
        $("#cv-additional").css("display", "block");
        $(".source-default-hidden").css("display", "none");
        $("#show-additional-sources").click(function() {
            $(".source-default-hidden").css("display", "");
            $("#cv-additional").css("display", "none");
            return false;
        });
    }
}

$(document).ready(function() {
    $(".oo-ui-optionWidget").click(selectTab);
    $("#compare-add-url").click(addUrl);
    $("#compare-paste").click(pasteText);
    $("#compare-upload").click(uploadFile);
    $(".compare-remove-url").click(removeUrl);

    setResultSelectionHandlers();

    $(".source-num-included").click(toggleSource);

    $(".cv-chain-cell .cv-hl").click(selectRegion);
    $("body").click(unselectRegions);

    $(document).keyup(function(e) {
         if (e.key === "Escape") {
            return unselectRegions();
        }
    });

    $("#cv-form").submit(submitForm);

    hideAdditionalSources();

    setNotice();
});
