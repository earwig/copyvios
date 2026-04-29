import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask

app = Flask(
    "copyvios",
    instance_path=os.getcwd(),
    instance_relative_config=True,
)

app.config.from_pyfile("config.py")
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(logging.DEBUG)
app.logger.addHandler(hand)
