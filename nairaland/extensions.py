"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_pymongo import PyMongo
from nairaland.commons.apispec import APISpecExt

mongo = PyMongo()
jwt = JWTManager()
apispec = APISpecExt()
