from flask import Blueprint, redirect, request
from flask.helpers import get_debug_flag
from spotify.settings import DevConfig, ProdConfig
from urllib.parse import urlencode

blueprint = Blueprint("routes", __name__)
CONFIG = DevConfig if get_debug_flag() else ProdConfig


@blueprint.route("/")
def index():
    return "This is a root placeholder"


@blueprint.route("/login")
def login():
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
        }
    )

    url = f"{provider_url}?{params}"

    return redirect(url)


@blueprint.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    print(f"received code: {code}")
    return "Received a callback"
