import sqlite3


def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    # 1. Категории
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    # 2. Поставщики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    ''')
    
    # 3. Товары
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            category_id INTEGER,
            supplier_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES Categories(id),
            FOREIGN KEY (supplier_id) REFERENCES Suppliers(id)
        )
    ''')
    
    # 4. Клиенты
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    
    # 5. Заказы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_datetime TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            delivery_method TEXT NOT NULL DEFAULT 'pickup',
            total_amount REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Новый',
            FOREIGN KEY (customer_id) REFERENCES Customers(id)
        )
    ''')
    
    # 6. Детали заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price_at_moment REAL NOT NULL CHECK(price_at_moment >= 0),
            FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    ''')
    
    # 7. Поставки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            delivery_datetime TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Ожидается',
            FOREIGN KEY (supplier_id) REFERENCES Suppliers(id)
        )
    ''')
    
    # 8. Детали поставок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DeliveryDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price_per_unit REAL NOT NULL CHECK(price_per_unit >= 0),
            FOREIGN KEY (delivery_id) REFERENCES Deliveries(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    ''')
    
    # 9. Пользователи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Администратор', 'Менеджер', 'Кассир-кладовщик')),
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'Администратор'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Users (username, password, full_name, role, is_active) VALUES 
            ('admin', 'admin123', 'Системный Администратор', 'Администратор', 1)
        ''')
    
    conn.commit()
    conn.close()


def get_all(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_by_id(table_name, record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        conn.close()


def delete_record(table_name, record_id):
    return execute_query(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))


if __name__ == "__main__":
    init_db()