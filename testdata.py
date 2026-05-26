from datetime import datetime
from database import execute_query, get_db_connection


class TestDataLoader:
    def __init__(self, models):
        self.category_model = models['category']
        self.supplier_model = models['supplier']
        self.product_model = models['product']
        self.customer_model = models['customer']
        self.order_model = models['order']
        self.order_detail_model = models['order_detail']
        self.delivery_model = models['delivery']
        self.delivery_detail_model = models['delivery_detail']
    
    def load_all(self):
        self.load_categories()
        self.load_suppliers()
        self.load_products()
        self.load_customers()
        self.load_orders()
        self.load_order_details()
        self.load_deliveries()
        self.load_delivery_details()
    
    def load_categories(self):
        categories = [
            ('Смартфоны', 'Мобильные телефоны и аксессуары'),
            ('Ноутбуки', 'Ноутбуки, ультрабуки, игровые ноутбуки'),
            ('Планшеты', 'Планшеты и электронные книги'),
            ('Аудиотехника', 'Наушники, колонки, плееры'),
            ('Фототехника', 'Фотоаппараты, объективы, штативы'),
            ('Аксессуары', 'Чехлы, зарядные устройства, кабели'),
            ('Комплектующие', 'Процессоры, видеокарты, память')
        ]
        for name, desc in categories:
            self.category_model.add(name, desc)
    
    def load_suppliers(self):
        suppliers = [
            ('Apple', '+7(495)111-22-33', 'apple@mail.ru', 'Москва, ул. Тверская, 10'),
            ('Samsung', '+7(495)222-33-44', 'samsung@mail.ru', 'Москва, ул. Ленина, 25'),
            ('Xiaomi', '+7(812)333-44-55', 'xiaomi@mail.ru', 'Санкт-Петербург, Невский пр., 5'),
            ('Sony', '+7(495)444-55-66', None, 'Москва, ул. Пушкина, 8'),
            ('JBL', None, 'jbl@mail.ru', 'Казань, ул. Центральная, 15'),
            ('ASUS', '+7(812)555-66-77', 'asus@mail.ru', 'Санкт-Петербург, Московское ш., 42'),
            ('HP', '+7(495)666-77-88', 'hp@mail.ru', 'Москва, ул. Садовая, 3'),
            ('Logitech', None, 'logitech@mail.ru', 'Нижний Новгород, ул. Советская, 7')
        ]
        for name, phone, email, address in suppliers:
            self.supplier_model.add(name, phone, email, address)
    
    def load_products(self):
        products = [
            ('iPhone 15 Pro', 99900, 50, 1, 1),
            ('iPhone 15', 79900, 60, 1, 1),
            ('Samsung Galaxy S24', 89900, 40, 1, 2),
            ('Xiaomi 14', 59900, 70, 1, 3),
            ('MacBook Pro 14"', 199900, 20, 2, 1),
            ('ASUS ROG Zephyrus', 149900, 25, 2, 6),
            ('HP Pavilion', 79900, 35, 2, 7),
            ('iPad Pro 11"', 89900, 45, 3, 1),
            ('Samsung Tab S9', 79900, 30, 3, 2),
            ('Xiaomi Pad 6', 39900, 50, 3, 3),
            ('AirPods Pro 2', 24900, 100, 4, 1),
            ('Samsung Buds2 Pro', 19900, 80, 4, 2),
            ('JBL Charge 5', 15900, 60, 4, 5),
            ('Sony WH-1000XM5', 34900, 40, 4, 4),
            ('Чехол для iPhone', 1990, 200, 6, 1),
            ('Зарядное устройство 65W', 2990, 150, 6, 6),
            ('Кабель USB-C', 990, 300, 6, 5),
            ('Защитное стекло', 990, 250, 6, 1),
            ('SSD 1TB', 8990, 80, 7, 7),
            ('Оперативная память 16GB', 5990, 100, 7, 6),
            ('Видеокарта RTX 4060', 49900, 30, 7, 6)
        ]
        for name, price, qty, cat_id, sup_id in products:
            self.product_model.add(name, price, qty, cat_id, sup_id)
    
    def load_customers(self):
        customers = [
            ('Иванов Иван Иванович', '+7(916)111-22-33', 'ivanov@mail.ru'),
            ('Петров Петр Петрович', '+7(916)444-55-66', 'petrov@mail.ru'),
            ('Сидорова Анна Сергеевна', '+7(916)777-88-99', 'sidorova@mail.ru'),
            ('Кузнецов Дмитрий', '+7(495)123-45-67', 'kuznetsov@mail.ru'),
            ('Михайлова Ольга', '+7(812)987-65-43', 'mikhailova@mail.ru'),
            ('Соколов Алексей', '+7(921)555-44-33', 'sokolov@mail.ru'),
            ('Новикова Екатерина', '+7(903)888-77-66', 'novikova@mail.ru'),
            ('Морозов Владимир', '+7(926)333-22-11', 'morozov@mail.ru'),
            ('Волкова Татьяна', None, 'volkova@mail.ru'),
            ('Зайцев Александр', '+7(909)111-99-88', None)
        ]
        for name, phone, email in customers:
            self.customer_model.add(name, phone, email)
    
    def load_orders(self):
        orders = [
            (1, "2026-05-01 10:30:00", 'delivery', 'Доставлен'),
            (2, "2026-05-02 14:15:00", 'pickup', 'Выдан'),
            (3, "2026-05-05 09:45:00", 'delivery', 'Отправлен'),
            (4, "2026-05-07 16:20:00", 'pickup', 'Обработан'),
            (5, "2026-05-10 11:00:00", 'delivery', 'Новый'),
            (1, "2026-05-12 13:30:00", 'pickup', 'Новый'),
            (6, "2026-05-15 15:45:00", 'delivery', 'Обработан'),
            (7, "2026-05-18 10:00:00", 'pickup', 'Доставлен'),
            (8, "2026-05-20 12:15:00", 'delivery', 'Отменён'),
            (9, "2026-05-22 14:30:00", 'pickup', 'Новый'),
            (10, "2026-05-25 09:00:00", 'delivery', 'Новый'),
            (3, "2026-05-27 16:45:00", 'pickup', 'Обработан'),
            (4, "2026-05-28 11:30:00", 'delivery', 'Отправлен'),
            (5, "2026-05-29 13:15:00", 'pickup', 'Доставлен'),
            (2, "2026-05-30 15:00:00", 'delivery', 'Доставлен')
        ]
        for cust_id, dt, method, status in orders:
            self.order_model.add(cust_id, dt, method)
    
    def load_order_details(self):
        order_details = [
            (1, 1, 1, 99900),
            (1, 15, 2, 1990),
            (2, 3, 1, 89900),
            (2, 12, 2, 19900),
            (3, 5, 1, 199900),
            (3, 19, 1, 8990),
            (4, 4, 2, 59900),
            (4, 20, 2, 5990),
            (5, 2, 1, 79900),
            (5, 16, 1, 2990),
            (6, 1, 1, 99900),
            (6, 18, 3, 990),
            (7, 6, 1, 149900),
            (7, 21, 1, 49900),
            (8, 8, 1, 89900),
            (8, 14, 1, 34900)
        ]
        for order_id, prod_id, qty, price in order_details:
            product = self.product_model.get_by_id(prod_id)
            if product and product['quantity'] >= qty:
                execute_query(
                    "INSERT INTO OrderDetails (order_id, product_id, quantity, price_at_moment) VALUES (?, ?, ?, ?)",
                    (order_id, prod_id, qty, price)
                )
                execute_query("UPDATE Products SET quantity = quantity - ? WHERE id = ?", (qty, prod_id))
        
        for order_id, _, _, _ in order_details:
            self.order_model.update_total(order_id)
    
    def load_deliveries(self):
        deliveries = [
            (1, "2026-05-01 09:00:00", 'Завершена'),
            (2, "2026-05-03 11:30:00", 'Завершена'),
            (3, "2026-05-06 14:45:00", 'В пути'),
            (4, "2026-05-08 10:15:00", 'Ожидается'),
            (5, "2026-05-11 16:00:00", 'Завершена'),
            (6, "2026-05-13 12:30:00", 'Ожидается'),
            (7, "2026-05-16 09:45:00", 'В пути'),
            (8, "2026-05-19 15:20:00", 'Ожидается'),
            (9, "2026-05-21 11:00:00", 'Завершена'),
            (10, "2026-05-23 13:30:00", 'Ожидается'),
            (1, "2026-05-25 10:00:00", 'В пути'),
            (3, "2026-05-27 14:30:00", 'Завершена')
        ]
        for sup_id, dt, status in deliveries:
            self.delivery_model.add(sup_id, dt)
    
    def load_delivery_details(self):
        delivery_details = [
            (1, 1, 10, 95000),
            (1, 2, 15, 75000),
            (2, 3, 20, 85000),
            (2, 5, 5, 190000),
            (3, 4, 25, 55000),
            (3, 8, 10, 85000),
            (4, 6, 15, 140000),
            (4, 7, 20, 75000),
            (5, 9, 30, 35000),
            (5, 10, 25, 75000),
            (6, 11, 50, 22000),
            (6, 12, 40, 18000)
        ]
        for del_id, prod_id, qty, price in delivery_details:
            execute_query(
                "INSERT INTO DeliveryDetails (delivery_id, product_id, quantity, price_per_unit) VALUES (?, ?, ?, ?)",
                (del_id, prod_id, qty, price)
            )
            execute_query("UPDATE Products SET quantity = quantity + ? WHERE id = ?", (qty, prod_id))
        
        for del_id, _, _, _ in delivery_details:
            self.delivery_model.update_total(del_id)
    def clear_all(self):
        execute_query("DELETE FROM OrderDetails")
        execute_query("DELETE FROM DeliveryDetails")
        execute_query("DELETE FROM Orders")
        execute_query("DELETE FROM Deliveries")
        execute_query("DELETE FROM Products")
        execute_query("DELETE FROM Customers")
        execute_query("DELETE FROM Suppliers")
        execute_query("DELETE FROM Categories") 