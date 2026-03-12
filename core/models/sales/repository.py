from datetime import datetime

def register_sale(db, total, operator, discount, fee, change, dt=None):
    if dt is None: 
        dt = datetime.now()
    
    normalized_dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO sales (total, datetime, operator_id, discount, fees_applied, change) VALUES (?, ?, ?, ?, ?, ?)",
        (float(total), normalized_dt, operator, discount, fee, change)
    )
    db.commit()

    sale_id = cursor.lastrowid
    return sale_id


def get_sale_details(db, sale_id):
    # Dados da venda + operador
    sale = db.execute("""
        SELECT s.id AS sale_id, s.total, s.datetime, s.discount, s.fees_applied, s.change, u.username AS operator
        FROM sales s
        JOIN users u ON s.operator_id = u.id
        WHERE s.id = ?
    """, (sale_id,)).fetchone()

    # Itens vendidos
    items = db.execute("""
    SELECT p.product_name,
           ps.subtotal,
           ps.quantity,
           (ps.subtotal / ps.quantity) AS unit_price
    FROM products_sold ps
    JOIN products p ON ps.product_id = p.id
    WHERE ps.sale_id = ?
    """, (sale_id,)).fetchall()


    # Pagamentos
    payments = db.execute("""
        SELECT method, value_paid
        FROM payments
        WHERE sale_id = ?
    """, (sale_id,)).fetchall()

    return sale, items, payments

    
def get_sales(db):
    sql = """
        SELECT 
            s.id,
            s.datetime,
            s.total,
            s.discount,
            s.fees_applied,
            s.change,
            u.username AS operator_name
        FROM sales s
        JOIN users u ON s.operator_id = u.id;
    """
    cursor = db.execute(sql)
    return cursor.fetchall()

