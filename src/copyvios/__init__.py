import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask

app = Flask("copyvios")

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(logging.DEBUG)
app.logger.addHandler(hand)
