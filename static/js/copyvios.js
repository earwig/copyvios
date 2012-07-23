// Thanks to http://www.quirksmode.org/js/cookies.html for the cookie code.

function get_cookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(";");
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == " ") {
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) == 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function set_cookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    }
    else {
        var expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/~earwig";
}

function delete_cookie(name) {
    set_cookie(name, "", -1);
}

function copyvio_toggle_details(details) {
    link = document.getElementById("cv-result-detail-link");
    details = document.getElementById("cv-result-detail");

    if (link.innerHTML == "Show details:") {
        details.style.display = "block";
        link.innerHTML = "Hide details:";
        set_cookie("EarwigCVShowDetails", "True", 180);
    } else {
        details.style.display = "none";
        link.innerHTML = "Show details:";
        if (get_cookie("EarwigCVShowDetails")) {
            delete_cookie("EarwigCVShowDetails");
        }
    }
}
