from flask import Blueprint, request, jsonify
import sqlite3
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies, JWTManager
import json

import core.common.responses as http
from core.common.auth import require_permission, create_profile_token
from core.security import hash_password, check_password
from core.common.db import get_db, select_cols_from_table
import core.models.users.repository as repo
from datetime import timedelta
from core.__init__ import jwt

users_bp = Blueprint("users", __name__)

@jwt.user_identity_loader
def user_identity_lookup(identity):
    return json.dumps(identity)

@users_bp.route("/login", methods=["POST"])
def authenticate():
    data = request.json
    username = data["username"]
    password = data["password"]

    username = str(username).lower()

    with get_db() as db:
        cursor = db.execute("SELECT password_hash, id, isAdmin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row and check_password(password, row[0]):
            expires = timedelta(hours=6)
            identity = {"username": username, "id": int(row[1])}
            access_token = create_access_token(identity=identity, expires_delta=expires)

            profile_token = create_profile_token(username, row[1], row[2])

            resp = jsonify({"message": "login realizado com sucesso", 
                            "profile_token":profile_token})
            
            set_access_cookies(resp, access_token)
            return resp, 200

        else:
            return http.http_error("Credenciais inválidas", 401)


@users_bp.route("/users", methods=["GET"])
@jwt_required()
@require_permission()
def get_users():
    try:
        with get_db() as db:
            users = select_cols_from_table(db, ["username", "isAdmin", "created_at"], "users")
            result = [{"username": row[0], "is_admin": row[1], "created_at": row[2]} for row in users]
            return jsonify(result)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)


@users_bp.route("/users", methods=["POST"])
@jwt_required()
@require_permission()
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    admin_status = 1 if str(data.get("is_admin")) == "1" else 0

    if not username or not password:
        return http.bad_request("username e password são parâmetros obrigatórios.")
    
    try:
        username = str(username).lower()
        with get_db() as db:
            password = hash_password(password)
            repo.insert_user(db, username, password, admin_status)
            return http.send_response("Usuário registrado com sucesso", 201)
    
    except sqlite3.IntegrityError:
        return http.bad_request("O username é inválido pois já está sendo utilizado.")
    
    except sqlite3.Error as e:
        return http.http_error(e, 500)


@users_bp.route("/users", methods=["PUT"])
@jwt_required()
@require_permission()
def update_password():
    username = request.json.get('username')
    new_password = request.json.get('password')

    if not username or not new_password:
        return http.bad_request("username e password são parâmetros obrigatórios.")
    
    try:
        with get_db() as db:
            password = hash_password(new_password)
            repo.update_user_password(db, username, password)
            return http.send_response(f"A senha de {username} foi alterada com sucesso.", 200)
    
    except sqlite3.Error as e:
        return http.http_error(e, 500)


@users_bp.route("/users", methods=["DELETE"])
@jwt_required()
@require_permission()
def delete_user():
    username = request.json.get('username')

    if not username:
        return http.bad_request("username é obrigatório")
    
    try:
        with get_db() as db:
            if repo.delete_user(db, username):
                return http.send_response(f"O usuário {username} foi deletado.", 200)
            else:
                return http.http_error(f"Usuário não encontrado", 404)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)

@users_bp.route("/users/<int:user_id>", methods=["GET"])
def detail_user(user_id):
    try:
        with get_db() as db:
            result = repo.detail_user(db, user_id)
            return jsonify(result)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)
    

@users_bp.route("/users/roles", methods=["POST"])
def assign_role():
    role = request.json.get("role_id")
    user = request.json.get("username")

    if not role or not user:
        return http.bad_request("role_id e username são obrigatórios para atribuição de um cargo")
    
    try:
        with get_db() as db:
            result = repo.user_assign_role(db, role, user)
            return jsonify(result)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)
