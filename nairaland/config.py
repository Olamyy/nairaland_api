"""Default configuration

Use env var to override
"""
import os

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

MONGODB_DB = 'nairaland'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

MONGO_URI = "mongodb://localhost:27017/nairaland"

JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
