import json
import os

from asana import Client
from flask import jsonify, request, session, url_for
from flask_socketio import emit

from .. import socketio
from . import main

client_id, client_secret = os.environ["ASANA_CLIENT"].split(":")


def init_client():
    return Client.oauth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for("main.callback", _external=True),
    )


@socketio.on("authenticate", namespace="/asana")
def authenticate():
    url = init_client().session.authorization_url()
    emit("verification", url[0], namespace="/asana")


@main.route("/asana/update", methods=["GET"])
def update_token():
    if request.args.get("token"):
        client = Client.oauth(
            token=json.loads(request.args["token"]),
            auto_refresh_url="https://app.asana.com/-/oauth_token",
            auto_refresh_kwargs={
                "client_id": client_id,
                "client_secret": client_secret,
            },
            token_updater=lambda token: session.__setitem__("asana_token", token),
        )
        client.users.get_user("me")  # arbitary request to trigger token_updater
        return jsonify(session.pop("asana_token"))
    return "No token provided", 400


@main.route("/asana/callback")
def callback():
    try:
        code = request.args.get("code")
        if not code:
            raise ValueError("Authentication unsuccessful.")

        token = init_client().session.fetch_token(code=code)
        socketio.emit("token", token, namespace="/asana")
        return (
            "Authentication successful! "
            "You may now close the browser tab and return to the application.",
            200,
        )
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

