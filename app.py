import json
import os

from asana import Client
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/asana2calendar"


def token_saver(token):
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def asana(request, client_id, client_secret):
    if request.args.get("token"):
        client = Client.oauth(
            token=json.loads(request.args["token"]),
            auto_refresh_url="https://app.asana.com/-/oauth_token",
            auto_refresh_kwargs={
                "client_id": client_id,
                "client_secret": client_secret,
            },
            token_updater=token_saver,
        )
        client.headers = {"asana-enable": "new_memberships"}
        client.users.get_user("me")  # arbitary request to trigger token_updater
        return jsonify(ACCESS_TOKEN)
    client = Client.oauth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    if request.args.get("code"):
        return jsonify(client.session.fetch_token(code=request.args["code"]))
    return jsonify(client.session.authorization_url())


@app.route("/callback", methods=["GET", "POST"])
def callback():
    if request.args.get("app") == "asana":
        client_id, client_secret = os.environ["ASANA_CLIENT"].split(":")
        return asana(request, client_id, client_secret)
    return "Invalid app name.", 400


@app.route("/")
def index():
    return render_template("index.html")
