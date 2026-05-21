import tkinter as tk
from tkinter import ttk, messagebox
from gui.products_tab import ProductsTab
from gui.categories_tab import CategoriesTab
from gui.suppliers_tab import SuppliersTab
from gui.customers_tab import CustomersTab
from gui.orders_tab import OrdersTab
from gui.deliveries_tab import DeliveriesTab
from gui.users_tab import UsersTab


class MainApp:
    def __init__(self, root, user_info):
        self.root = root
        self.user_role = user_info['role']
        self.user_info = user_info
        
        self.root.title(f"Строительный магазин - {user_info['full_name']}")
        self.root.geometry("1200x700")
        
        self.create_menu()
        self.create_notebook()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить все", command=self.refresh_all)
        file_menu.add_separator()
        
        if self.user_role == 'Администратор':
            file_menu.add_command(label="Загрузить тестовые данные", command=self.load_test_data)
            file_menu.add_command(label="Полная очистка всех данных", command=self.clear_all_data)
            file_menu.add_separator()
        
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчёты", menu=report_menu)
        report_menu.add_command(label="Топ товаров", command=self.show_top_products)
        report_menu.add_command(label="Продажи по категориям", command=self.show_sales_by_category)
        report_menu.add_command(label="Заказы за период", command=self.show_orders_by_period)
        report_menu.add_command(label="Низкий остаток", command=self.show_low_stock)
        report_menu.add_separator()
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
    
        # Сохраняем вкладки в переменные self
        self.products_tab = ProductsTab(self.notebook, self.user_role)
        self.categories_tab = CategoriesTab(self.notebook, self.user_role)
        self.suppliers_tab = SuppliersTab(self.notebook, self.user_role)
        self.customers_tab = CustomersTab(self.notebook, self.user_role)
        self.orders_tab = OrdersTab(self.notebook, self.user_role)
        self.deliveries_tab = DeliveriesTab(self.notebook, self.user_role)
    
        if self.user_role == 'Администратор':
            self.users_tab = UsersTab(self.notebook, self.user_role)
    
    def refresh_all(self):
        # Обновляем каждую вкладку напрямую
        self.products_tab.load_products()
        self.categories_tab.load_categories()
        self.suppliers_tab.load_suppliers()
        self.customers_tab.load_customers()
        self.orders_tab.load_orders()
        self.deliveries_tab.load_deliveries()
    
        if self.user_role == 'Администратор':
            self.users_tab.load_users()
    
        messagebox.showinfo("Успех", "Все данные обновлены")
    
    def load_test_data(self):
        print("Функция load_test_data вызвана")  # Добавьте для проверки
        if not messagebox.askyesno("Подтверждение", "Загрузить тестовые данные? Все текущие данные будут удалены!"):
            return
    
        from testdata import TestDataLoader
        from models import (
            CategoryModel, SupplierModel, ProductModel, CustomerModel,
            OrderModel, OrderDetailModel, DeliveryModel, DeliveryDetailModel
        )
    
        print("Импорт выполнен")  # Добавьте для проверки
    
        models = {
            'category': CategoryModel(),
            'supplier': SupplierModel(),
            'product': ProductModel(),
            'customer': CustomerModel(),
            'order': OrderModel(),
            'order_detail': OrderDetailModel(),
            'delivery': DeliveryModel(),
            'delivery_detail': DeliveryDetailModel()
        }
    
        print("Модели созданы")  # Добавьте для проверки
    
        loader = TestDataLoader(models)
        loader.load_all()
    
        print("Данные загружены")  # Добавьте для проверки
    
        self.refresh_all()
    
    def clear_all_data(self):
        if not messagebox.askyesno("Подтверждение", "Очистить все данные? Это действие необратимо!"):
            return
    
        try:
            from database import execute_query
        
            # Очищаем таблицы в правильном порядке (по зависимостям FOREIGN KEY)
            execute_query("DELETE FROM OrderDetails")
            execute_query("DELETE FROM DeliveryDetails")
            execute_query("DELETE FROM Orders")
            execute_query("DELETE FROM Deliveries")
            execute_query("DELETE FROM Products")
            execute_query("DELETE FROM Customers")
            execute_query("DELETE FROM Suppliers")
            execute_query("DELETE FROM Categories")
            execute_query("DELETE FROM sqlite_sequence")
        
            # Обновляем все вкладки
            self.refresh_all()
        
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при очистке: {e}")
    
    def show_top_products(self):
        from reports import ReportGenerator
        r = ReportGenerator()
        data = r.get_top_products()
        win = tk.Toplevel(self.root)
        win.title("Топ товаров")
        win.geometry("600x400")
        self._show_report_table(win, ('Товар', 'Продано', 'Выручка'), [(d['name'], d['total_sold'], d['revenue']) for d in data])
    
    def show_sales_by_category(self):
        from reports import ReportGenerator
        r = ReportGenerator()
        data = r.get_sales_by_category()
        win = tk.Toplevel(self.root)
        win.title("Продажи по категориям")
        win.geometry("600x400")
        self._show_report_table(win, ('Категория', 'Продано', 'Выручка'), [(d['name'], d['items_sold'], d['revenue']) for d in data])
    
    def show_orders_by_period(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Заказы за период")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        tk.Label(dialog, text="Начальная дата (ГГГГ-ММ-ДД):").pack(pady=5)
        start_entry = tk.Entry(dialog)
        start_entry.pack(pady=5)
        
        tk.Label(dialog, text="Конечная дата (ГГГГ-ММ-ДД):").pack(pady=5)
        end_entry = tk.Entry(dialog)
        end_entry.pack(pady=5)
        
        def show():
            from reports import ReportGenerator
            r = ReportGenerator()
            orders = r.get_orders_by_period(start_entry.get(), end_entry.get())
            win = tk.Toplevel(dialog)
            win.title(f"Заказы с {start_entry.get()} по {end_entry.get()}")
            win.geometry("800x500")
            self._show_report_table(win, ('ID', 'Клиент', 'Дата и время', 'Сумма', 'Статус'), 
                                   [(o['id'], o['customer'], o['order_datetime'], o['total_amount'], o['status']) for o in orders])
            #dialog.destroy()
        
        tk.Button(dialog, text="Показать", command=show).pack(pady=10)
    
    def show_low_stock(self):
        from reports import ReportGenerator
        r = ReportGenerator()
        data = r.get_low_stock_products()
        win = tk.Toplevel(self.root)
        win.title("Товары с низким остатком")
        win.geometry("700x500")
        self._show_report_table(win, ('Товар', 'Остаток', 'Цена', 'Категория'), [(d['name'], d['quantity'], d['price'], d['category']) for d in data])
    
    def _show_report_table(self, parent, headers, data):
        tree = ttk.Treeview(parent, columns=headers, show='headings', height=20)
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        for row in data:
            tree.insert('', 'end', values=row)