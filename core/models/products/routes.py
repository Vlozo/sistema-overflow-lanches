from flask import Blueprint, request, jsonify
import sqlite3
from flask_jwt_extended import jwt_required

from core.common import responses as http
from core.common.auth import require_permission, get_identity
from core.common.db import get_db, run_paginated_query
from core.common.normalize import parse_money, InvalidFormatError
import core.models.products.repository as repo

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["POST"])
@jwt_required()
@require_permission("create_product")
def register_product():
    product_code = request.json.get("code")
    product = request.json.get("product") or request.json.get("product_name")
    price  = request.json.get("price")
    cost = request.json.get("cost")

    operator = get_identity()

    if not product or not price or not product_code:
        return http.bad_request("Os campos 'code','product','price' são obrigatórios para o registro do produto.")
    
    try:
        cost = parse_money(cost) if cost else 0
        price = parse_money(price)
        with get_db() as db:
            repo.insert_product(db, operator["id"], product_code, product, price, cost)
            return http.send_response(f"O produto foi registrado com sucesso.", 201)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)
    
    except InvalidFormatError as e:
        return http.bad_request(e)
    
@products_bp.route("/products", methods=["GET"])
@jwt_required()
@require_permission("create_product")
def get_products():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("perPage", 10))
    search = str(request.args.get("search", "")).strip()

    db = get_db()

    base_query = """
        SELECT 
            p.id,
            p.code,
            p.product_name AS product,
            p.price,
            p.cost,
            p.created_at,
            p.last_updated,
            u.username AS updated_by
        FROM products p
        LEFT JOIN users u ON p.updated_by = u.id
    """

    count_query = "SELECT COUNT(*) AS count FROM products p"

    params = ()
    if search:
        base_query += " WHERE p.product_name LIKE ? OR p.code LIKE ?"
        count_query += " WHERE p.product_name LIKE ? OR p.code LIKE ?"
        like_pattern = f"%{search}%"
        params = (like_pattern, like_pattern)

    base_query += " ORDER BY p.id"

    result = run_paginated_query(db, base_query, count_query, params=params, page=page, per_page=per_page)

    for row in result["rows"]:
        row["price"] = f"{float(str(row['price']).replace(',', '.')):.2f}".replace(".", ",")
        row["cost"] = f"{float(str(row['cost']).replace(',', '.')):.2f}".replace(".", ",")

    db.close()
    return jsonify(result)

@products_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
@require_permission("update_product")
def update_product(product_id):
    data = request.json
    operator = get_identity()

    product = data.get("product")
    price = data.get("price")
    cost = data.get("cost")
    code = data.get("code")

    if not product:
        return http.bad_request("O campo 'product' é obrigatório")

    try:
        price = parse_money(price) if price else price
        cost = parse_money(cost) if cost else cost

        with get_db() as db:
            rows = repo.update_product(
                db,
                operator["id"],
                product_id,
                product,
                price,
                code,
                cost
            )
            if rows == 0:
                return http.http_error("Nenhum produto encontrado ou atualizado", 404)
            return http.send_response("O produto foi alterado com sucesso", 200)

    except sqlite3.IntegrityError:
        return http.http_error("Esse código já está em uso", 400)

    except sqlite3.Error as e:
        return http.http_error(str(e), 500)

    except InvalidFormatError as e:
        return http.bad_request(str(e))

@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
@require_permission("delete_product")
def delete_product(product_id):
    try:
        with get_db() as db:
            if repo.delete_product(db, product_id):
                return http.send_response("O produto foi deletado", 200)
            else:
                return http.http_error("Produto não encontrado", 404)
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)