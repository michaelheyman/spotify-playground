import base64
import random
import string
from urllib.parse import urlencode

import requests
from flask import Blueprint
from flask import redirect
from flask import request
from flask.helpers import get_debug_flag

from spotify.settings import DevConfig
from spotify.settings import ProdConfig

blueprint = Blueprint("routes", __name__)
CONFIG = DevConfig if get_debug_flag() else ProdConfig
STATE_KEY = "spotify_auth_state"


@blueprint.route("/")
def index():
    return "This is a root placeholder"


@blueprint.route("/login")
def login():
    state = random_string(16)
    provider_url = "https://accounts.spotify.com/authorize"
    scopes = [
        "playlist-modify-private",
        "playlist-read-private",
        "user-read-private",
        "user-read-email",
    ]
    params = urlencode(
        {
            "response_type": "code",
            "client_id": CONFIG.CLIENT_ID,
            "scope": " ".join(scopes),
            "redirect_uri": f"http://{CONFIG.SERVER_HOST}:{CONFIG.PORT}/callback",
            "state": state,
        }
    )
    url = f"{provider_url}?{params}"

    res = redirect(url)
    res.set_cookie(STATE_KEY, state)

    return res


@blueprint.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    stored_state = request.cookies.get(STATE_KEY) if request.cookies else None

    if not stored_state or state != stored_state:
        return f"State mismatch: expected '{stored_state}' but received '{state}'"

    try:
        access_token = request_access_token(code)
    except requests.exceptions.HTTPError as err:
        print(f"There was an error requesting the access token: {err}")
        return "There was an error requesting the access token"

    print(access_token)
    return "Received a callback and a token"


def request_access_token(code):
    url = "https://accounts.spotify.com/api/token"
    authorization = str(
        base64.b64encode(f"{CONFIG.CLIENT_ID}:{CONFIG.CLIENT_SECRET}".encode("utf-8")),
        "utf-8",
    )
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"http://{CONFIG.SERVER_HOST}:{CONFIG.PORT}/callback",
    }
    headers = {"Authorization": f"Basic {authorization}"}

    response = requests.request("POST", url, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    access_token = data["access_token"]
    return access_token


def random_string(length=10):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
    )
