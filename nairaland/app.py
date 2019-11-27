from flask import Flask

from nairaland import api
from nairaland.extensions import mongo, jwt, apispec


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('nairaland')
    app.config.from_object('nairaland.config')

    if testing is True:
        app.config['TESTING'] = True

    configure_extensions(app, cli)
    configure_apispec(app)
    register_blueprints(app)

    return app


def configure_extensions(app, cli):
    """configure flask extensions
    """
    mongo.init_app(app)
    jwt.init_app(app)


def configure_apispec(app):
    """Configure APISpec for swagger support
    """
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme("jwt", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    })
    apispec.spec.components.schema(
        "PaginatedResult", {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }})


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(api.views.blueprint)
