from flask import Blueprint, request, jsonify
import sqlite3
from flask_jwt_extended import jwt_required

from core.common import responses as http
from core.common.auth import require_permission
from core.common.db import get_db, select_all_from
import core.models.permissions.repository as repo

permissions_bp = Blueprint("permissions", __name__)

@permissions_bp.route("/permissions", methods=["POST"])
@jwt_required()
@require_permission()
def create_permissions():
    permissions = request.json.get("permissions")

    if not permissions or not isinstance(permissions, list):
        return http.bad_request("É necessário enviar uma lista 'permissions'.")

    values = [(perm["title"],) for perm in permissions if "title" in perm]

    if not values:
        return http.bad_request("Nenhuma permissão válida encontrada.")

    try: 
        with get_db() as db:
            repo.insert_permissions(db, values)
            return jsonify({
                "message": "Permissões criadas com sucesso",
                "permissions": [v[0] for v in values]
            })
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)

@permissions_bp.route("/permissions", methods=["GET"])
@jwt_required()
@require_permission()
def list_permissions():
    try:
        with get_db() as db:
            rows = select_all_from(db, "permissions")
            return jsonify([dict(row) for row in rows])

    except sqlite3.Error as e:
        return http.http_error(e, 500)