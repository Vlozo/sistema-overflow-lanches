import os
import sqlite3
from .security import hash_password
from .config import Config

DATABASE = Config.DATABASE_URL

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        base_dir = os.path.dirname(__file__)
        schema_path = os.path.join(base_dir, "schema.sql")
        
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        
        conn.execute("""
            INSERT INTO users (username, password_hash, isAdmin)
            VALUES (?, ?, ?)
        """, ("admin", hash_password(Config.ADMIN_PWD), 1))
        
        conn.commit()
        conn.close()
        set_permissions()

def set_permissions():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
            INSERT INTO permissions (title) VALUES 
            ("create_product"), ("read_product"), ("delete_product"), ("update_product"),
            ("view_cashflow"), ("register_sale")
        """)
    
    conn.commit()
    conn.close()
