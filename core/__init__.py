from flask import Flask
from .config import Config
from .security import jwt, bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
jwt.init_app(app)
CORS(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])

from . import main
