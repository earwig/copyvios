function potd_set_background() {
    var d = new Date();
    var callback = "like_a_boss";
    var date = (d.getUTCFullYear()) + "-" + zero_pad(d.getUTCMonth() + 1, 2) + "-" + zero_pad(d.getUTCDate(), 2);
    var base = "http://commons.wikimedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=Template:Potd/";
    var url = base + date + "&callback=" + callback;

    var script = document.createElement("script");
    var head = document.getElementsByTagName("head")[0];

    window[callback] = function(data) {
        head.removeChild(script);
        parse_file_name(data);
    };

    script.src = url;
    head.appendChild(script);
}

function parse_file_name(data) {
    var content = "";
    var res = data["query"]["pages"];
    for (pageid in res) {
        content = res[pageid]["revisions"][0]["*"];
    }
    var filename = /\{\{Potd filename\|(1=)?(.*?)\|.*?\}\}/.exec(content)[2];

    var callback = "like_a_faust";
    var base = "http://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size&format=json&titles=File:";
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
    var width = 1024,
        height = 768;
    if (document.body && document.body.offsetWidth && document.body.offsetHeight) {
        width = document.body.offsetWidth;
        height = document.body.offsetHeight;
    }
    if (document.compatMode=="CSS1Compat" && document.documentElement && document.documentElement.offsetWidth && document.documentElement.offsetHeight) {
        width = document.documentElement.offsetWidth;
        height = document.documentElement.offsetHeight;
    }
    if (window.innerWidth && window.innerHeight) {
        width = window.innerWidth;
        height = window.innerHeight;
    }
    return [width, height];
}
