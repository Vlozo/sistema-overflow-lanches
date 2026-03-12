from flask import Blueprint, request, jsonify
import sqlite3
from flask_jwt_extended import jwt_required
from decimal import Decimal
from datetime import datetime as dt

from core.common import responses as http
from core.common.auth import require_permission, get_identity
from core.common.db import get_db, run_paginated_query
from core.common.normalize import new_normalize_items, normalize_payment_method, parse_money, parse_js_date, InvalidFormatError
import core.models.sales.repository as repo
from core.models.products.repository import get_products_by_ids

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/sales", methods=["POST"])
@jwt_required()
@require_permission("register_sale")
def register_sale():
    user = get_identity()
    payment = request.json.get("payment")
    products_sold = request.json.get("items")
    datetime = request.json.get("sale_date")
    discount_data = request.json.get("discount")
    change_data = request.json.get("change")
    fee_data = request.json.get("fee")
    operator_id = user["id"]

    if not payment and not products_sold:
        return http.bad_request("'payment' e 'items' são campos obrigatórios.")
    
    if not isinstance(products_sold, list) or not isinstance(payment, list):
        return http.bad_request("O campo 'items' e o campo 'payment' deve ser uma lista de objetos")
    
    try:
        items = new_normalize_items(products_sold)
        payment_methods = normalize_payment_method(payment)

        discount = parse_money(discount_data) if discount_data else 0
        fee = parse_money(fee_data) if fee_data else 0
        change = parse_money(change_data) if change_data else 0
        datetime = parse_js_date(datetime)

        ids = [item["id"] for item in items]

        with get_db() as db:

            products = get_products_by_ids(db, ids)
            subtotal = Decimal("0.00")
            items_with_subtotals = []

            for item in items:
                product = next((p for p in products if p["id"] == item["id"]), None)
                if product:
                    price = Decimal(str(product["price"]))
                    item_subtotal = price * item["quantity"]
                    subtotal += item_subtotal

                    items_with_subtotals.append({
                        "id": item["id"],
                        "quantity": item["quantity"],
                        "unit_price": str(price),
                        "subtotal": str(item_subtotal)
                    })

            total = (subtotal - discount) + fee
            sale = repo.register_sale(
                db, total, operator_id, str(discount), str(fee), str(change), datetime
            )

            for item in items_with_subtotals:
                db.execute(
                    "INSERT INTO products_sold (sale_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                    (sale, item["id"], item["quantity"], item["subtotal"])
                )

            for payment in payment_methods:
                db.execute("INSERT INTO payments (sale_id, method, value_paid) VALUES (?, ?, ?)",
                           (sale, str(payment["method"]), str(payment["value"]))
                        )

            db.commit()

            response = {
                "sale_id": sale,
                "subtotal": str(subtotal),
                "discount": str(discount),
                "fee": str(fee),
                "change": str(change),
                "total": str(total),
                "sale_date": (datetime.strftime("%d-%m-%Y") if datetime else dt.now().strftime("%d-%m-%Y")),
                "operator": user["username"],
                "items": [
                    {
                        "id": item["id"],
                        "name": next((p["product_name"] for p in products if p["id"] == item["id"]), None),
                        "quantity": item["quantity"],
                        "unit_price": str(next((p["price"] for p in products if p["id"] == item["id"]), None))
                    }
                    for item in items
                ],
                "payments": [
                    {
                        "method": p["method"],
                        "value_paid": str(p["value"])
                    }
                    for p in payment_methods
                ]
            }

            return jsonify(response), 201
        
    except sqlite3.Error as e:
        return http.http_error(e, 500)
    
    except InvalidFormatError as e:
        return http.bad_request(e)

@sales_bp.route("/sales", methods=["GET"])
@jwt_required()
@require_permission("view_cashflow")
def get_sales():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("perPage", 10))
    search = str(request.args.get("search", "")).strip()

    db = get_db()

    base_query = """
        SELECT 
            s.id,
            s.total,
            s.discount,
            s.change,
            s.fees_applied,
            s.datetime,
            u.username as operator
        FROM sales s
        LEFT JOIN users u ON s.operator_id = u.id
    """

    count_query = "SELECT COUNT(*) AS count FROM sales s"

    params = ()
    if search:
        base_query += " WHERE s.id LIKE ?"
        count_query += " WHERE s.id LIKE ?"
        like_pattern = f"{search}%"
        params = (like_pattern,)

    base_query += " ORDER BY s.datetime DESC"

    result = run_paginated_query(db, base_query, count_query, params=params, page=page, per_page=per_page)

    for row in result["rows"]:
        row["total"] = f"{float(str(row['total']).replace(',', '.')):.2f}".replace(".", ",")
        row["discount"] = f"{float(str(row['discount']).replace(',', '.')):.2f}".replace(".", ",")
        row["change"] = f"{float(str(row['change']).replace(',', '.')):.2f}".replace(".", ",")
        row["fees_applied"] = f"{float(str(row['fees_applied']).replace(',', '.')):.2f}".replace(".", ",")
        row["datetime"] = ( 
            dt.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y') if row['datetime'] else "undefined"
        )

    db.close()
    return jsonify(result)


@sales_bp.route("/sales/<int:sale_id>", methods=["GET"])
@jwt_required()
@require_permission("view_cashflow")
def get_sale_details(sale_id):
    try:
        with get_db() as db:
            sale, items, payments = repo.get_sale_details(db, sale_id)

            if not sale:
                return http.bad_request(f"Nenhuma venda encontrada com id {sale_id}")
            
            t, d, f = float(sale["total"]), float(sale["discount"]), float(sale["fees_applied"])

            sale_subtotal = (t - f) + d

            response = {
                "sale_id": sale["sale_id"],
                "subtotal": str(sale_subtotal),
                "total": str(sale["total"]),
                "fees_applied": str(sale["fees_applied"]),
                "change": str(sale["change"]),
                "discount" : str(sale["discount"]),
                "datetime": sale["datetime"],
                "operator": sale["operator"],
                "items": [dict(row) for row in items],
                "payments": [dict(row) for row in payments]
            }
            return response

    except sqlite3.Error as e:
        return http.http_error(e, 500)