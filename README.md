This is a [copyright violation](https://en.wikipedia.org/wiki/WP:COPYVIO)
detector running on [Wikimedia Labs](https://tools.wmflabs.org/copyvios).

It can search the web for content similar to a given article, and graphically
compare an article to a specific URL.

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

- Install all dependencies listed above. You might want to use a
  [virtualenv](http://virtualenv.readthedocs.org/).
- Create the SQL database defined in `schema.sql`. Also create the `cache` and
  `cache_data` tables defined by
  [earwigbot-plugins](https://github.com/earwig/earwigbot-plugins/blob/develop/tasks/schema/afc_copyvios.sql);
  this can be in the same or a different database.
- Create an earwigbot instance in `.earwigbot` (run `earwigbot .earwigbot`). In
  `.earwigbot/config.yml`, fill out the connection info for the database(s)
  above by adding the following to the `wiki` section:
        _copyviosSQL:
            globals:
                host: <hostname of database defined in schema.sql>
                db:   <name of database>
            cache:
                host: <hostname of database containing cache and cache_data tables>
                db:   <name of database>
  If additional arguments are needed by `oursql.connect()`, like usernames or
  passwords, they should be added to the `globals` and `cache` sections.
- Copy `.lighttpd.conf` to the relevant location (on Tool Labs, this is in the
  root of the project's home directory) and adjust its contents as necessary.
- Run `./build.py` to minify JS and CSS files.
- Adjust the hashbang in `app.fcgi` to point to the correct Python interpreter
  or virtual environment.
- Start lighttpd (on Tool Labs, `webservice start`).
