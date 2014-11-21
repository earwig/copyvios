function update_screen_size() {
    var cache = cache_cookie();
    var data = {
        "width": window.screen.availWidth,
        "height": window.screen.availHeight
    }
    if (!cache || cache["width"] != data["width"] || cache["height"] != data["height"]) {
        set_cookie("CopyviosScreenCache", JSON.stringify(data), 1095);
    }
}

function cache_cookie() {
    var cookie = get_cookie("CopyviosScreenCache");
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

function get_cookie(name) {
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

function set_cookie_with_date(name, value, date) {
    value = window.btoa("--cpv2" + value);
    var path = window.location.pathname.split("/", 2)[1];
    if (date) {
        var expires = "; expires=" + date.toUTCString();
    }
    else {
        var expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/" + path;
}

function set_cookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        set_cookie_with_date(name, value, date);
    }
    else {
        set_cookie_with_date(name, value);
    }
}

function delete_cookie(name) {
    set_cookie(name, "", -1);
}

$(document).ready(function() {
    $("#action-search").change(function() {
        $(".cv-search").prop("disabled", false);
        $(".cv-compare").prop("disabled", true);
    });
    $("#action-compare").change(function() {
        $(".cv-search").prop("disabled", true);
        $(".cv-compare").prop("disabled", false);
    });

    if ($("#action-search" ).is(":checked")) $("#action-search" ).change();
    if ($("#action-compare").is(":checked")) $("#action-compare").change();

    $("#cv-form").submit(function() {
        if ($("#action-search").is(":checked")) {
            if ($("#cv-cb-engine").is(":checked"))
                $(".cv-search[type='hidden'][name='use_engine']").prop("disabled", true);
            if ($("#cv-cb-links").is(":checked"))
                $(".cv-search[type='hidden'][name='use_links']").prop("disabled", true);
        }
    });

    if ($("#cv-additional").length) {
        $("#cv-additional").css("display", "block");
        $(".source-default-hidden").css("display", "none");
        $("#show-additional-sources").click(function() {
            $(".source-default-hidden").css("display", "");
            $("#cv-additional").css("display", "none");
            return false;
        });
    }
});
