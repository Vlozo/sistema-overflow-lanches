
def insert_permissions(db, title):
    db.executemany( "INSERT OR IGNORE INTO permissions (title) VALUES (?)", title) 
    db.commit()