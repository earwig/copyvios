function set_background_potd() {
    if (cache_cookie()) return;
    var d = new Date();
    var callback = "earwigpotd1";
    var date = (d.getUTCFullYear()) + "-" + zero_pad(d.getUTCMonth() + 1, 2) + "-" + zero_pad(d.getUTCDate(), 2);
    var base = "//commons.wikimedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Template:Potd/";
    var url = base + date + "&callback=" + callback;

    var script = document.createElement("script");
    var head = document.getElementsByTagName("head")[0];

    window[callback] = function(data) {
        head.removeChild(script);
        parse_potd_file_name(data);
    };

    script.src = url;
    head.appendChild(script);
}

function set_background_list() {
    if (cache_cookie()) return;
    var base = "//commons.wikimedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=User:The+Earwig/POTD";
    var url = base + "&callback=" + callback;

    var script = document.createElement("script");
    var head = document.getElementsByTagName("head")[0];

    window[callback] = function(data) {
        head.removeChild(script);
        parse_list_file_name(data);
    };

    script.src = url;
    head.appendChild(script);
}

function cache_cookie() {
    var cookie = get_cookie("EarwigBackgroundCache");
    if (cookie) {
        try {
            data = JSON.parse(cookie);
            var filename = data.filename;
            var url = data.url;
            var descurl = data.descurl;
            var imgwidth = data.imgwidth;
            var imgheight = data.imgheight;
            if (filename && url && descurl && imgwidth && imgheight) {
                set_background(filename, url, descurl, imgwidth, imgheight);
                return true;
            }
        }
        catch (SyntaxError) {}
    }
    return false;
}

function parse_potd_file_name(data) {
    var content = "";
    var res = data["query"]["pages"];
    for (pageid in res) {
        content = res[pageid]["revisions"][0]["*"];
    }
    var filename = /\{\{Potd filename\|(1=)?(.*?)\|.*?\}\}/.exec(content)[2];

    var callback = "earwigpotd2";
    var base = "//commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size&format=json&titles=File:";
    var url = base + escape(filename) + "&callback=" + callback;

    var script = document.createElement("script");
    var head = document.getElementsByTagName("head")[0];

    window[callback] = function(data) {
        head.removeChild(script);
        parse_file_url(data, escape(filename.replace(/ /g, "_")));
    };

    script.src = url;
    head.appendChild(script);
}

function parse_list_file_name(data) {
    var content = "";
    var res = data["query"]["pages"];
    for (pageid in res) {
        content = res[pageid]["revisions"][0]["*"];
    }

    var filenames = [];
    while ((match = /\*\s*\[\[File:(.*?)\]\]/g.exec(content)) !== null) {
        filenames.push(match[1]);
    }
    var filename = filenames[Math.floor(Math.random() * filenames.length)];

    var callback = "earwigpotd2";
    var base = "//commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size&format=json&titles=File:";
    var url = base + escape(filename) + "&callback=" + callback;

    var script = document.createElement("script");
    var head = document.getElementsByTagName("head")[0];

    window[callback] = function(data) {
        head.removeChild(script);
        parse_file_url(data, escape(filename.replace(/ /g, "_")));
    };

    script.src = url;
    head.appendChild(script);
}

function parse_file_url(data, filename) {
    var url = "";
    var descurl = "";
    var imgwidth = 1024;
    var imgheight = 768;

    var res = data["query"]["pages"];
    for (pageid in res) {
        r = res[pageid]["imageinfo"][0];
        url = r["url"];
        descurl = r["descriptionurl"];
        imgwidth = r["width"];
        imgheight = r["height"];
    }

    set_background(filename, url, descurl, imgwidth, imgheight);
    var data = {"filename": filename, "url": url, "descurl": descurl, "imgwidth": imgwidth, "imgheight": imgheight};
    var expires = new Date();
    expires.setUTCMilliseconds(0);
    expires.setUTCSeconds(0);
    expires.setUTCMinutes(0);
    expires.setUTCHours(0);
    expires.setUTCDate(expires.getUTCDate() + 1);
    set_cookie_with_date("EarwigBackgroundCache", JSON.stringify(data), expires);
}

function set_background(filename, url, descurl, imgwidth, imgheight) {
    var s = get_window_size();
    var winwidth = s[0];
    var winheight = s[1];

    var width = winwidth;
    if (imgwidth/imgheight > winwidth/winheight) {
        width = Math.round((imgwidth/imgheight) * winheight);
    }
    if (width >= imgwidth) {
        document.body.style.backgroundImage = "url('" + url + "')";
        if (width > imgwidth) {
            document.body.style.setProperty("background-size", "cover");
        }
    } else {
        url = url.replace(/\/commons\//, "/commons/thumb/") + "/" + width + "px-" + filename;
        document.body.style.backgroundImage = "url('" + url + "')";
    }
    document.getElementById("bg_image_link").href = descurl;
}

function zero_pad(value, length) {
    value = String(value);
	length = length || 2;
	while (value.length < length) {
	    value = "0" + value;
    }
	return value;
}

function get_window_size() {
    // See http://www.javascripter.net/faq/browserw.htm
    if (document.body && document.body.offsetWidth && document.body.offsetHeight) {
        return [document.body.offsetWidth, document.body.offsetHeight];
    }
    if (document.compatMode=="CSS1Compat" && document.documentElement && document.documentElement.offsetWidth && document.documentElement.offsetHeight) {
        return [document.documentElement.offsetWidth, document.documentElement.offsetHeight];
    }
    if (window.innerWidth && window.innerHeight) {
        return [window.innerWidth, window.innerHeight];
    }
    return [1024, 768];
}
