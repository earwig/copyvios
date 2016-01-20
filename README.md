This is a [copyright violation](https://en.wikipedia.org/wiki/WP:COPYVIO)
detector running on [Wikimedia Labs](https://tools.wmflabs.org/copyvios).

It can search the web for content similar to a given article, and graphically
compare an article to a specific URL. Some technical details are expanded upon
[in a blog post](http://benkurtovic.com/2014/08/20/copyvio-detector.html).

Dependencies
============

* [earwigbot](https://github.com/earwig/earwigbot) >= 0.1
* [flask](http://flask.pocoo.org/) >= 0.10.1
* [flask-mako](https://pythonhosted.org/Flask-Mako/) >= 0.3
* [mako](http://www.makotemplates.org/) >= 0.7.2
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell) >= 0.3
* [oursql](http://packages.python.org/oursql/) >= 0.9.3.1
* [requests](http://python-requests.org/) >= 2.9.1
* [SQLAlchemy](http://sqlalchemy.org/) >= 0.9.6
* [uglifycss](https://github.com/fmarcia/UglifyCSS/)
* [uglifyjs](https://github.com/mishoo/UglifyJS/) >= 1.3.3

Running
=======

- If using Tool Labs, you should clone the repository to `~/www/python/src`, or
  otherwise symlink it to that directory. A
  [virtualenv](http://virtualenv.readthedocs.org/) should be created at
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

- Start the web server (on Tool Labs, `webservice2 uwsgi-python start`).
