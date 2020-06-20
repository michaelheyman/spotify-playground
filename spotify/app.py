from flask import Flask
from spotify.settings import ProdConfig
from spotify import routes


def create_app(config_object=ProdConfig):
    """ Creates a Flask application and initializes its internal components
    :return: a Flask application
    """

    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    register_blueprints(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(routes.blueprint)
