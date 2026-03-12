
def insert_user(db, username, password_hash, is_admin=False):
    db.execute(
        "INSERT INTO users (username, password_hash, isAdmin) VALUES (?, ?, ?)",
        (username, password_hash, is_admin)
    )
    db.commit()

def update_user_password(db, username, password):
    db.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password, username))
    db.commit()

def delete_user(db, username):
    cursor = db.execute("DELETE FROM users WHERE username = ?", (username,))
    db.commit()
    return cursor.rowcount > 0

def user_assign_role(db, role_id, username):
    user = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        raise ValueError("Usuário não encontrado")

    user_id = user["id"]

    db.execute(
        "INSERT OR IGNORE INTO user_roles (role_id, user_id) VALUES (?, ?)",
        (role_id, user_id)
    )
    db.commit()

    result = db.execute("""
        SELECT u.username, r.name AS role_name
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN role r ON ur.role_id = r.id
        WHERE u.id = ? AND r.id = ?
    """, (user_id, role_id)).fetchone()

    if result:
        return dict(result)
    return None

def detail_user(db, user_id):
    user = db.execute(
        "SELECT id, username, created_at, isAdmin FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user:
        raise ValueError("Usuário não encontrado")

    roles = db.execute("""
        SELECT r.name AS role_name
        FROM user_roles ur
        JOIN role r ON ur.role_id = r.id
        WHERE ur.user_id = ?
    """, (user_id,)).fetchall()

    role_names = [row["role_name"] for row in roles]

    return {
        "id": user["id"],
        "username": user["username"],
        "created_at": user["created_at"],
        "isAdmin": bool(user["isAdmin"]),
        "roles": role_names
    }