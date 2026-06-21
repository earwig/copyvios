import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from toolforge_i18n import ToolforgeI18n, set_user_agent


class CopyviosSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        if request.endpoint == "static" and request.args.get("v"):
            return False
        return super().should_set_cookie(app, session)


class CopyviosFlask(Flask):
    session_interface = CopyviosSessionInterface()

    def get_send_file_max_age(self, filename: str | None) -> int | None:
        if request.args.get("v"):
            return 365 * 24 * 60 * 60
        return super().get_send_file_max_age(filename)


app = CopyviosFlask(
    "copyvios",
    instance_path=os.getcwd(),
    instance_relative_config=True,
)

app.config.from_pyfile("config.py")
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)

set_user_agent(
    "Copyvios/1.0 (https://github.com/earwig/copyvios; tools.copyvios@toolforge.org)"
)
i18n = ToolforgeI18n(app)

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(logging.DEBUG)
app.logger.addHandler(hand)
