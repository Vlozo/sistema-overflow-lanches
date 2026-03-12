from flask import Flask
from .config import Config
from .security import jwt, bcrypt
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
jwt.init_app(app)
CORS(app, supports_credentials=True, origins=["http://192.168.1.71:8080", "http://localhost:8080"])

from . import main  # importa rotas/views
