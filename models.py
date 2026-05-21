from database import get_db_connection, execute_query, get_all, get_by_id, delete_record


class BaseModel:
    def __init__(self, table_name):
        self.table_name = table_name
    
    def get_all(self):
        return get_all(self.table_name)
    
    def get_by_id(self, record_id):
        return get_by_id(self.table_name, record_id)
    
    def delete(self, record_id):
        return delete_record(self.table_name, record_id)


class CategoryModel(BaseModel):
    def __init__(self):
        super().__init__('Categories')
    
    def add(self, name, description=None):
        return execute_query(
            "INSERT INTO Categories (name, description) VALUES (?, ?)",
            (name, description)
        )
    
    def update(self, category_id, name, description=None):
        return execute_query(
            "UPDATE Categories SET name = ?, description = ? WHERE id = ?",
            (name, description, category_id)
        )


class SupplierModel(BaseModel):
    def __init__(self):
        super().__init__('Suppliers')
    
    def add(self, name, phone=None, email=None, address=None):
        return execute_query(
            "INSERT INTO Suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address)
        )
    
    def update(self, supplier_id, name, phone=None, email=None, address=None):
        return execute_query(
            "UPDATE Suppliers SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?",
            (name, phone, email, address, supplier_id)
        )


class ProductModel(BaseModel):
    def __init__(self):
        super().__init__('Products')
    
    def add(self, name, price, quantity, category_id, supplier_id=None):
        return execute_query(
            "INSERT INTO Products (name, price, quantity, category_id, supplier_id) VALUES (?, ?, ?, ?, ?)",
            (name, price, quantity, category_id, supplier_id)
        )
    
    def update(self, product_id, name, price, quantity, category_id, supplier_id=None):
        return execute_query(
            "UPDATE Products SET name = ?, price = ?, quantity = ?, category_id = ?, supplier_id = ? WHERE id = ?",
            (name, price, quantity, category_id, supplier_id, product_id)
        )
    
    def search(self, keyword):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE name LIKE ?", (f'%{keyword}%',))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_low_stock(self, threshold=10):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE quantity <= ?", (threshold,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class CustomerModel(BaseModel):
    def __init__(self):
        super().__init__('Customers')
    
    def add(self, name, phone=None, email=None):
        return execute_query(
            "INSERT INTO Customers (name, phone, email) VALUES (?, ?, ?)",
            (name, phone, email)
        )
    
    def update(self, customer_id, name, phone=None, email=None):
        return execute_query(
            "UPDATE Customers SET name = ?, phone = ?, email = ? WHERE id = ?",
            (name, phone, email, customer_id)
        )


class OrderModel(BaseModel):
    def __init__(self):
        super().__init__('Orders')
    
    def add(self, customer_id, order_datetime, delivery_method='pickup'):
        return execute_query(
            "INSERT INTO Orders (customer_id, order_datetime, delivery_method, status) VALUES (?, ?, ?, 'Новый')",
            (customer_id, order_datetime, delivery_method)
        )
    
    def update_status(self, order_id, status):
        return execute_query(
            "UPDATE Orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
    
    def update_total(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(quantity * price_at_moment) as total FROM OrderDetails WHERE order_id = ?", (order_id,))
        result = cursor.fetchone()
        total = result['total'] if result and result['total'] else 0
        
        cursor.execute("UPDATE Orders SET total_amount = ? WHERE id = ?", (total, order_id))
        conn.commit()
        conn.close()
        return total


class OrderDetailModel(BaseModel):
    def __init__(self):
        super().__init__('OrderDetails')
    
    def add(self, order_id, product_id, quantity, price_at_moment):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM Orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order or order['status'] in ['Отправлен', 'Доставлен', 'Отменён']:
            conn.close()
            return False
        
        cursor.execute("SELECT quantity FROM Products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product or product['quantity'] < quantity:
            conn.close()
            return False
        
        cursor.execute(
            "INSERT INTO OrderDetails (order_id, product_id, quantity, price_at_moment) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, price_at_moment)
        )
        
        cursor.execute("UPDATE Products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
        
        conn.commit()
        conn.close()
        
        order_model = OrderModel()
        order_model.update_total(order_id)
        
        return True
    
    def get_by_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT od.*, p.name as product_name 
            FROM OrderDetails od 
            JOIN Products p ON od.product_id = p.id 
            WHERE od.order_id = ?
        """, (order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def remove_item(self, detail_id, order_id, product_name, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
    
        cursor.execute("SELECT id FROM Products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
    
        if not product:
            conn.close()
            return False
    
        cursor.execute("UPDATE Products SET quantity = quantity + ? WHERE id = ?", (quantity, product['id']))
        cursor.execute("DELETE FROM OrderDetails WHERE id = ?", (detail_id,))
    
        conn.commit()
        conn.close()
    
        order_model = OrderModel()
        order_model.update_total(order_id)
    
        return True



class DeliveryModel(BaseModel):
    def __init__(self):
        super().__init__('Deliveries')
    
    def add(self, supplier_id, delivery_datetime):
        return execute_query(
            "INSERT INTO Deliveries (supplier_id, delivery_datetime, status) VALUES (?, ?, 'Ожидается')",
            (supplier_id, delivery_datetime)
        )
    
    def update_status(self, delivery_id, status):
        return execute_query(
            "UPDATE Deliveries SET status = ? WHERE id = ?",
            (status, delivery_id)
        )
    
    def update_total(self, delivery_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(quantity * price_per_unit) as total FROM DeliveryDetails WHERE delivery_id = ?", (delivery_id,))
        result = cursor.fetchone()
        total = result['total'] if result and result['total'] else 0
        
        cursor.execute("UPDATE Deliveries SET total_amount = ? WHERE id = ?", (total, delivery_id))
        conn.commit()
        conn.close()
        return total


class DeliveryDetailModel(BaseModel):
    def __init__(self):
        super().__init__('DeliveryDetails')
    
    def add(self, delivery_id, product_id, quantity, price_per_unit):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM Deliveries WHERE id = ?", (delivery_id,))
        delivery = cursor.fetchone()
        
        if not delivery or delivery['status'] in ['Завершена', 'Отменена']:
            conn.close()
            return False
        
        cursor.execute(
            "INSERT INTO DeliveryDetails (delivery_id, product_id, quantity, price_per_unit) VALUES (?, ?, ?, ?)",
            (delivery_id, product_id, quantity, price_per_unit)
        )
        
        cursor.execute("UPDATE Products SET quantity = quantity + ? WHERE id = ?", (quantity, product_id))
        
        conn.commit()
        conn.close()
        
        delivery_model = DeliveryModel()
        delivery_model.update_total(delivery_id)
        
        return True
    
    def get_by_delivery(self, delivery_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dd.*, p.name as product_name 
            FROM DeliveryDetails dd 
            JOIN Products p ON dd.product_id = p.id 
            WHERE dd.delivery_id = ?
        """, (delivery_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    def remove_item(self, detail_id, delivery_id, product_name, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM Products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
    
        if not product:
            conn.close()
            return False

        cursor.execute("UPDATE Products SET quantity = quantity - ? WHERE id = ?", (quantity, product['id']))

        cursor.execute("DELETE FROM DeliveryDetails WHERE id = ?", (detail_id,))
    
        conn.commit()
        conn.close()

        delivery_model = DeliveryModel()
        delivery_model.update_total(delivery_id)
    
        return True


class UserModel(BaseModel):
    def __init__(self):
        super().__init__('Users')
    
    def add(self, username, password, full_name, role, is_active=1):
        return execute_query(
            "INSERT INTO Users (username, password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?)",
            (username, password, full_name, role, is_active)
        )
    
    def update(self, user_id, username, full_name, role, is_active=1):
        return execute_query(
            "UPDATE Users SET username = ?, full_name = ?, role = ?, is_active = ? WHERE id = ?",
            (username, full_name, role, is_active, user_id)
        )
    
    def change_password(self, user_id, new_password):
        return execute_query(
            "UPDATE Users SET password = ? WHERE id = ?",
            (new_password, user_id)
        )
    
    def authenticate(self, username, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, full_name, role FROM Users WHERE username = ? AND password = ? AND is_active = 1",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None