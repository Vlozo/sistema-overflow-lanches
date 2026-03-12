import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

def value_not_definied(key):
    return RuntimeError(f"{key} não definido no ambiente.")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
    
    PROFILE_SECRET = os.getenv("PROFILE_SECRET")
    if not PROFILE_SECRET:
        raise value_not_definied("PROFILE_SECRET")

    PEPPER = os.getenv("PEPPER_KEY")
    if not PEPPER:
        raise value_not_definied("PEPPER_KEY")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") 
    if not JWT_SECRET_KEY: 
        raise value_not_definied("JWT_SECRET_KEY")
    
    ADMIN_PWD = os.getenv("ADMIN_PWD")
    if not ADMIN_PWD:
        raise value_not_definied("ADMIN_PWD")
    
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_SESSION_COOKIE = False
    JWT_COOKIE_HTTPONLY = True

    # OPÇÃO A: Localhost sem HTTPS (Recomendado para Dev)
    JWT_COOKIE_SAMESITE = "Lax" 
    JWT_COOKIE_SECURE = False 
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True

