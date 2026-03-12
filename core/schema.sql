CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    isAdmin INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT (datetime('now','-3 hours'))
);

CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code INTEGER UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    cost REAL NOT NULL,
    price REAL NOT NULL,
    created_at DATETIME DEFAULT (datetime('now','-3 hours')), 
    last_updated DATETIME DEFAULT (datetime('now','-3 hours')),
    updated_by INTEGER NOT NULL,
    FOREIGN KEY (updated_by) REFERENCES users (id)
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL,
    discount REAL NOT NULL,
    fees_applied REAL NOT NULL,
	change REAL NOT NULL,
    datetime TEXT NOT NULL,
    operator_id INTEGER NOT NULL,
    FOREIGN KEY (operator_id) REFERENCES users (id)
);

CREATE TABLE products_sold (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    sale_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (sale_id) REFERENCES sales (id)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    method VARCHAR NOT NULL,
    value_paid VARCHAR NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales (id)
);

CREATE TABLE role (
	id INTEGER PRIMARY KEY,
	name VARCHAR NOT NULL UNIQUE,
	created_at DATETIME DEFAULT (datetime('now','-3 hours'))
);

CREATE TABLE permissions (
	id INTEGER PRIMARY KEY,
	title VARCHAR UNIQUE NOT NULL
);

CREATE TABLE role_permissions (
    role_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES role(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

CREATE TABLE user_roles (
    user_id INTEGER,
    role_id INTEGER,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES role(id)
);

CREATE TRIGGER update_last_updated
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    UPDATE products
    SET last_updated = datetime('now','-3 hours')
    WHERE id = OLD.id;
END;
