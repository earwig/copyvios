This is a [copyright violation](https://en.wikipedia.org/wiki/WP:COPYVIO)
detector web tool for Wikipedia articles running on
[Wikimedia Cloud Services](https://wikitech.wikimedia.org/wiki/Help:Cloud_Services_introduction)
at [copyvios.toolforge.org](https://copyvios.toolforge.org/).

It can search the web for content similar to a given article, and graphically
compare an article to specific URLs. Some technical details are expanded upon
[in a blog post](https://benkurtovic.com/2014/08/20/copyvio-detector.html),
though much of it is outdated.

Installation
============

- If using Toolforge, clone the repository to `~/www/python/src`, or otherwise
  symlink it to that directory.

- Create a virtual environment and install the dependencies. On Toolforge,
  this should be in `~/www/python/venv`, otherwise it can be in a subdirectory
  of the git project named `venv`:

      python3 -m venv venv
      . venv/bin/activate
      pip install -e .

- If you intend to modify CSS or JS, install the frontend dependencies:

      npm install -g uglify-js cssnano postcss postcss-cli

- Create an SQL database with the tables defined by `schema.sql`.

- Create an earwigbot instance in `.earwigbot` (run `earwigbot .earwigbot`).
  In `.earwigbot/config.yml`, fill out the connection info for the database by
  adding the following to the `wiki` section:

      copyvios:
        oauth:
          consumer_token: <oauth consumer token>
          consumer_secret: <oauth consumer secret>
        sql:
          engine: mysql
          host: <hostname of database server>
          db: <name of database>

Running
=======

- Run `make` to minify JS and CSS files after making any frontend changes.

- Start your WSGI server pointing to app:app. For production, uWSGI or
  Gunicorn are likely good options. For development, use `flask run`.
