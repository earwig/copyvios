This is a [copyright violation](https://en.wikipedia.org/wiki/WP:COPYVIO)
detector running on [Wikimedia Labs](https://tools.wmflabs.org/copyvios).

It works by searching the web for page content, or comparing an article to a
specific URL.

Dependencies
============

* [earwigbot](https://github.com/earwig/earwigbot) >= 0.1
* [flask](http://flask.pocoo.org/) >= 0.10.1
* [flask-mako](https://pythonhosted.org/Flask-Mako/) >= 0.3
* [flup](http://trac.saddi.com/flup) >= 1.0.3
* [mako](http://www.makotemplates.org/) >= 0.7.2
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell) >= 0.3
* [oursql](http://packages.python.org/oursql/) >= 0.9.3.1
* [SQLAlchemy](http://sqlalchemy.org/) >= 0.9.6
* [uglifycss](https://github.com/fmarcia/UglifyCSS/)
* [uglifyjs](https://github.com/mishoo/UglifyJS/) >= 1.3.3

Running
=======

- Install all dependencies.
- Copy `.lighttpd.conf` to the relevant location.
- Run `./build.py` to minify JS and CSS files.
- Start lighttpd.
