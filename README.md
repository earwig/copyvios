This is a [copyright violation](https://en.wikipedia.org/wiki/WP:COPYVIO)
detector running on [Wikimedia Cloud Services](https://copyvios.toolforge.org/).

It can search the web for content similar to a given article, and graphically
compare an article to a specific URL. Some technical details are expanded upon
[in a blog post](https://benkurtovic.com/2014/08/20/copyvio-detector.html).

Dependencies
============

* [earwigbot](https://github.com/earwig/earwigbot) >= 0.1
* [flask](https://flask.palletsprojects.com/) >= 0.10.1
* [flask-mako](https://pythonhosted.org/Flask-Mako/) >= 0.3
* [mako](https://www.makotemplates.org/) >= 0.7.2
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell) >= 0.3
* [mwoauth](https://github.com/mediawiki-utilities/python-mwoauth) == 0.3.8
* [oursql](https://pythonhosted.org/oursql/) >= 0.9.3.1
* [requests](https://requests.readthedocs.io/) >= 2.9.1
* [SQLAlchemy](https://www.sqlalchemy.org/) >= 0.9.6
* [apsw](https://github.com/rogerbinns/apsw) >= 3.26.0
* [uglifyjs](https://github.com/mishoo/UglifyJS) >= 3.12.6
* [cssnano](https://github.com/cssnano/cssnano) >= 4.1.10
* [postcss-cli](https://github.com/postcss/postcss-cli) >= 8.3.1

Running
=======

- If using Toolforge, you should clone the repository to `~/www/python/src`, or
  otherwise symlink it to that directory. A
  [virtualenv](https://virtualenv.pypa.io/) should be created at
  `~/www/python/venv`.

- Install all dependencies listed above.

- Create an SQL database with the `cache` and `cache_data` tables defined by
  [earwigbot-plugins](https://github.com/earwig/earwigbot-plugins/blob/develop/tasks/schema/afc_copyvios.sql).

- Create an earwigbot instance in `.earwigbot` (run `earwigbot .earwigbot`). In
  `.earwigbot/config.yml`, fill out the connection info for the database by
  adding the following to the `wiki` section:

        _copyviosSQL:
            host: <hostname of database server>
            db:   <name of database>

  If additional arguments are needed by `oursql.connect()`, like usernames or
  passwords, they should be added to the `_copyviosSQL` section.

- Run `./build.py` to minify JS and CSS files.

- Start the web server (on Toolforge, `webservice uwsgi-python start`).
