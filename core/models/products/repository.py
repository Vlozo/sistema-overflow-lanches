
def insert_product(db, operator, code, product, price, cost):
    db.execute("INSERT INTO products (code, product_name, price, cost, updated_by) VALUES (?, ?, ?, ?, ?)", (code, product, str(price), str(cost), operator))
    db.commit

def update_product(db, operator, product_id, product = None, price = None, new_code = None, cost = None):
    fields = []
    values = []

    if product is not None:
        fields.append("product_name = ?")
        values.append(product)

    if price is not None:
        fields.append("price = ?")
        values.append(str(price))
    
    if cost is not None:
        fields.append("cost = ?")
        values.append(str(cost))
    
    if new_code is not None:
        fields.append("code = ?")
        values.append(int(new_code))

    if not fields:
        return

    fields.append(f"updated_by = ?")
    values.append(int(operator))
    sql = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"
    values.append(product_id)

    cursor = db.execute(sql, values)
    db.commit()

    return cursor.rowcount
    
def delete_product(db, product_id):
    cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    return cursor.rowcount > 0
    
def get_products_by_ids(db, ids):
    placeholders = ",".join("?" for _ in ids)
    sql = f"SELECT * FROM products WHERE id IN ({placeholders})"
    cursor = db.cursor()
    cursor.execute(sql, ids)
    return [dict(row) for row in cursor.fetchall()]