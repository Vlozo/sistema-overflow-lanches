
def user_has_permission(db, username, permission_name):
    query = """
    SELECT COUNT(*)
    FROM users u
    JOIN user_roles ur ON u.id = ur.user_id
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    WHERE u.username = ? AND p.title = ?
    """
    cursor = db.execute(query, (username, permission_name))
    return cursor.fetchone()[0] > 0


def create_role(db, role):
    db.execute("INSERT INTO role (name) VALUES (?)", (role,))
    db.commit()


def detail_role(db, role_id):
    role = db.execute(
        "SELECT id, name, created_at FROM role WHERE id = ?",
        (role_id,)
    ).fetchone()

    if not role:
        raise ValueError("Cargo não encontrado")

    permissions = db.execute("""
        SELECT p.id, p.title
        FROM role_permissions rp
        JOIN permissions p ON rp.permission_id = p.id
        WHERE rp.role_id = ?
    """, (role_id,)).fetchall()

    permission_list = [dict(p) for p in permissions]

    return {
        "id": role["id"],
        "name": role["name"],
        "created_at": role["created_at"],
        "permissions": permission_list
    }

def assign_permissions(db, values: list[str]):
        db.executemany( "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", values) 
        db.commit()