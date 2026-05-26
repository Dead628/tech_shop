from database import get_db_connection


class ReportGenerator:
    def __init__(self):
        pass
    
    def get_top_products(self, limit=5):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, SUM(od.quantity) as total_sold, SUM(od.quantity * od.price_at_moment) as revenue
            FROM OrderDetails od
            JOIN Products p ON od.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_sales_by_category(self):
        """Продажи по категориям"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name, SUM(od.quantity) as items_sold, SUM(od.quantity * od.price_at_moment) as revenue
            FROM Categories c
            JOIN Products p ON p.category_id = c.id
            JOIN OrderDetails od ON od.product_id = p.id
            GROUP BY c.id, c.name
            ORDER BY revenue DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_orders_by_period(self, start_date, end_date):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, c.name as customer, o.order_datetime, o.total_amount, o.status
            FROM Orders o
            JOIN Customers c ON c.id = o.customer_id
            WHERE DATE(o.order_datetime) BETWEEN ? AND ?
            ORDER BY o.order_datetime DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_low_stock_products(self, threshold=10):
        """Товары с низким остатком"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.quantity, p.price, c.name as category
            FROM Products p
            JOIN Categories c ON c.id = p.category_id
            WHERE p.quantity <= ?
            ORDER BY p.quantity ASC
        """, (threshold,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]