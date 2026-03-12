# roles/routes.py
from flask import Blueprint, request, jsonify
import sqlite3
from flask_jwt_extended import jwt_required

from core.common import responses as http
from core.common.auth import require_permission
from core.common.db import get_db, select_all_from
import core.models.roles.repository as repo

roles_bp = Blueprint("roles", __name__)

@roles_bp.route("/roles", methods=["GET"])
@jwt_required()
@require_permission()
def get_roles():
    try:
        with get_db() as db:
            roles = select_all_from(db, "role")
            return jsonify([dict(row) for row in roles])
        
    except sqlite3.Error as e:
        return http.http_error(e,500)

@roles_bp.route("/roles", methods=["POST"])
@jwt_required()
@require_permission()
def create_role():
    role = request.json.get("role")

    if not role:
        return http.bad_request("O campo 'role' é obrigatório para a criação de um cargo")

    try:
        with get_db() as db:
            repo.create_role(db, role)
            return http.send_response(f"O cargo de {role} foi criado com sucesso", 201)
    
    except sqlite3.Error as e:
        return http.http_error(e, 500)
    
@roles_bp.route("/roles/<int:role_id>", methods=["GET"])
@jwt_required()
@require_permission()
def role_detail(role_id):
    try:
        with get_db() as db:
            result = repo.detail_role(db, role_id)
            return jsonify(result)
    except sqlite3.Error as e:
        return http.http_error(e, 500)

@roles_bp.route("/roles/permissions", methods=["POST"])
def set_role_permissions():
    role = request.json.get("role_id")
    permissions = request.json.get("permissions_id")

    if not role:
        return http.bad_request("'role_id' é obrigatório para a atribuição de permissões ao cargo.")
    if not permissions or not isinstance(permissions, list):
        return http.bad_request("É necessário enviar uma lista 'permissions_id'.")
    
    values = [(role, perm_id) for perm_id in permissions]

    try:
        with get_db() as db:
            repo.assign_permissions(db, values)
            result = repo.detail_role(db, role)
            return jsonify(result)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)