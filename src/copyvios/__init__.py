import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, Response, request


class CopyviosFlask(Flask):
    def get_send_file_max_age(self, filename: str | None) -> int | None:
        if request.args.get("v"):
            return 365 * 24 * 60 * 60
        return super().get_send_file_max_age(filename)

    def send_static_file(self, filename: str) -> Response:
        response = super().send_static_file(filename)
        response.headers.pop("Set-Cookie", None)
        return response


app = CopyviosFlask(
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
