import os

from flask import Flask
from flask_session import Session

from spotify import routes
from spotify.settings import ProdConfig


def create_app(config_object=ProdConfig):
    """ Creates a Flask application and initializes its internal components
    :return: a Flask application
    """

    app = Flask(__name__.split(".")[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    app.config["SECRET_KEY"] = os.urandom(64)
    app.config["SESSION_TYPE"] = "filesystem"
    register_blueprints(app)

    Session(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(routes.blueprint)
