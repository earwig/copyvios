import mwoauth
from flask import session, request
from .misc import cache

__all__ = ["oauth_login_start", "oauth_login_end", "clear_login_session"]

def oauth_login_start():
    consumer_token = mwoauth.ConsumerToken(
        cache.bot.config.wiki["copyvios"]["oauth"]["consumer_token"],
        cache.bot.config.wiki["copyvios"]["oauth"]["consumer_secret"])

    redirect, request_token = mwoauth.initiate(
        "https://meta.wikimedia.org/w/index.php", consumer_token)
    session["request_token"] = dict(zip(request_token._fields, request_token))

    # Take note of where to send the user after logging in
    next_url = (request.form if request.method == "POST" else request.args).get("next", "/")
    if next_url[0] == "/":
        # Only allow internal redirects
        session["next"] = next_url

    return redirect

def oauth_login_end():
    if "request_token" not in session:
        raise ValueError("OAuth request token not found in session.")

    consumer_token = mwoauth.ConsumerToken(
        cache.bot.config.wiki["copyvios"]["oauth"]["consumer_token"],
        cache.bot.config.wiki["copyvios"]["oauth"]["consumer_secret"])

    access_token = mwoauth.complete(
        "https://meta.wikimedia.org/w/index.php",
        consumer_token,
        mwoauth.RequestToken(**session["request_token"]),
        request.query_string)
    identity = mwoauth.identify(
        "https://meta.wikimedia.org/w/index.php",
        consumer_token,
        access_token)

    session["access_token"] = dict(zip(access_token._fields, access_token))
    session["username"] = identity["username"]

    return session.get("next", "/")

def clear_login_session():
    session.clear()