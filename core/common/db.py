import sqlite3
from flask import g

DATABASE = "database.db"
WHITELIST = ["products", "sales", "users", "role", "permissions", "user_profiles", "products_sold"]

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def select_all_from(db, table: str):
    """Função de uso exclusivo para interpolação interna, nunca receber parâmetros vindo diretamente de requisições HTTP"""
    if table not in WHITELIST:
        raise ValueError("Tabela não permitida")
        
    return db.execute(f"SELECT * FROM {table}").fetchall()
    
def select_cols_from_table(db, cols: list[str], table: str):
    """Função de uso exclusivo para interpolação interna, nunca receber parâmetros vindo diretamente de requisições HTTP"""
    if table not in WHITELIST:
        raise ValueError("Tabela não permitida")
        
    cols = ", ".join(cols)
    return db.execute(f"SELECT {cols} FROM {table}").fetchall()

def run_paginated_query(db, base_query: str, count_query: str, params: tuple = (), page: int = 1, per_page: int = 10):
    cursor = db.cursor()

    cursor.execute(count_query, params) 
    total_items = cursor.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page

    offset = (page - 1) * per_page
    paginated_query = f"{base_query} LIMIT ? OFFSET ?"

    if not isinstance(params, tuple):
        params = tuple(params)


    final_params = params + (per_page, offset)

    cursor.execute(paginated_query, final_params)

    rows = cursor.fetchall()
    items = [dict(row) for row in rows] 

    cursor.close()

    return {
        "rows": items,
        "totalPages": total_pages,
        "currentPage": page
    }
