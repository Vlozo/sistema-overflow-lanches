import os
import sqlite3
from .security import hash_password
from .config import Config

DATABASE = Config.DATABASE_URL

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        with open("core/schema.sql", "r") as f:
            conn.executescript(f.read())
        
        # usuário admin inicial
        conn.execute("""
            INSERT INTO users (username, password_hash, isAdmin)
            VALUES (?, ?, ?)
        """, ("admin", hash_password(Config.ADMIN_PWD), 1))

        set_permissions()

        conn.commit()
        conn.close()

def set_permissions():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
            INSERT INTO permissions (title) VALUES 
            ("create_product"), ("read_product"), ("delete_product"), ("update_product"),
            ("view_cashflow"), ("register_sale")
        """)
    
    conn.commit()
    conn.close()