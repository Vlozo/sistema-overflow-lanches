from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .config import Config
from flask import request
import hmac, hashlib

bcrypt = Bcrypt()
jwt = JWTManager()

def hash_password(password: str) -> str:
    pre_hash = hmac.new(Config.PEPPER.encode(), password.encode(), hashlib.sha256).digest()
    return bcrypt.generate_password_hash(pre_hash).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    pre_hash = hmac.new(Config.PEPPER.encode(), password.encode(), hashlib.sha256).digest()
    return bcrypt.check_password_hash(hashed, pre_hash)