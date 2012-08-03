function update_screen_size() {
    var cache = cache_cookie();
    var data = {
        "width": window.screen.availWidth,
        "height": window.screen.availHeight
    }
    if (!cache || cache["width"] != data["width"] || cache["height"] != data["height"]) {
        set_cookie("EarwigScreenCache", JSON.stringify(data), 1095);
    }
}

function cache_cookie() {
    var cookie = get_cookie("EarwigScreenCache");
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
