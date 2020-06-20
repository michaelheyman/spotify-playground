"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    try:
        CLIENT_ID = os.environ['CLIENT_ID']
    except KeyError:
        raise EnvironmentError('CLIENT_ID needs to be set to connect to Spotify') from KeyError

    try:
        CLIENT_SECRET = os.environ['CLIENT_SECRET']
    except KeyError:
        raise EnvironmentError('CLIENT_SECRET needs to be set to connect to Spotify') from KeyError

    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SERVER_HOST = os.environ.get('SERVER_HOST', 'localhost')
    PORT = int(os.environ.get('SERVER_PORT', '5000'))


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
