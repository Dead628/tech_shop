import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import OrderModel, OrderDetailModel, CustomerModel, ProductModel


class OrdersTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.order_model = OrderModel()
        self.order_detail_model = OrderDetailModel()
        self.customer_model = CustomerModel()
        self.product_model = ProductModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Заказы")
        
        self.create_widgets()
        self.load_orders()
    
    def create_widgets(self):
        top = ttk.Frame(self.tab)
        top.pack(fill='both', expand=True)
        
        cols = ('ID', 'Клиент', 'Дата и время', 'Сумма', 'Статус')
        self.orders_tree = ttk.Treeview(top, columns=cols, show='headings', height=10)
        col_widths = [50, 200, 180, 120, 150]
        for col, w in zip(cols, col_widths):
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=w)
        self.orders_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        bf = ttk.Frame(top)
        bf.pack(pady=5)
        ttk.Button(bf, text="Новый заказ", command=self.create_order).pack(side='left', padx=5)
        ttk.Button(bf, text="Изменить статус", command=self.change_order_status).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_orders).pack(side='left', padx=5)
        
        bottom = ttk.LabelFrame(self.tab, text="Детали заказа")
        bottom.pack(fill='both', expand=True)
        
        detail_cols = ('ID', 'Товар', 'Количество', 'Цена', 'Сумма')
        self.detail_tree = ttk.Treeview(bottom, columns=detail_cols, show='headings', height=8)
        detail_widths = [50, 250, 100, 100, 120]
        for col, w in zip(detail_cols, detail_widths):
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=w)
        self.detail_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(bottom)
        btn_frame.pack(pady=5)
    
        ttk.Button(btn_frame, text="Добавить товар", command=self.add_order_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить товар", command=self.remove_order_item).pack(side='left', padx=5)
   

        self.orders_tree.bind('<<TreeviewSelect>>', self.load_order_details)
    
    def load_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        for o in self.order_model.get_all():
            c = self.customer_model.get_by_id(o['customer_id'])
            self.orders_tree.insert('', 'end', values=(
                o['id'], c['name'] if c else 'Нет', o['order_datetime'], o['total_amount'], o['status']
            ))
    
    def load_order_details(self, event):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        sel = self.orders_tree.selection()
        if not sel:
            return
        
        oid = self.orders_tree.item(sel[0])['values'][0]
        for d in self.order_detail_model.get_by_order(oid):
            self.detail_tree.insert('', 'end', values=(
                d['id'], d['product_name'], d['quantity'], d['price_at_moment'],
                d['quantity'] * d['price_at_moment']
            ))
    
    def create_order(self):
        if self.user_role not in ['Администратор', 'Менеджер']:
            messagebox.showerror("Ошибка", "У вас нет прав на создание заказов")
            return
        customers = self.customer_model.get_all()
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Новый заказ")
        dialog.geometry("400x250")
        dialog.grab_set()
        
        tk.Label(dialog, text="Клиент:").pack(pady=10)
        customer_combo = ttk.Combobox(dialog, values=[c['name'] for c in customers], width=30)
        customer_combo.pack(pady=5)
        
        tk.Label(dialog, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ:СС):").pack(pady=5)
        date_entry = tk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        date_entry.pack(pady=5)
        
        def save():
            selected = customer_combo.get()
            for c in customers:
                if c['name'] == selected:
                    self.order_model.add(c['id'], date_entry.get())
                    break
            dialog.destroy()
            self.load_orders()
            messagebox.showinfo("Успех", "Заказ создан")
        
        tk.Button(dialog, text="Создать", command=save).pack(pady=20)
    
    def add_order_item(self):
        if self.user_role not in ['Администратор', 'Менеджер']:
            messagebox.showerror("Ошибка", "У вас нет прав на создание заказов")
            return
        sel = self.orders_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Сначала выберите заказ")
            return
        
        oid = self.orders_tree.item(sel[0])['values'][0]
        products = self.product_model.get_all()
        status = self.orders_tree.item(sel[0])['values'][4]
        if status in ['Отправлен', 'Доставлен', 'Отменён']:
            messagebox.showwarning("Внимание", f"Нельзя добавлять товары в заказ со статусом '{status}'")        
            return

        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить товар в заказ")
        dialog.geometry("400x250")
        dialog.grab_set()
        
        tk.Label(dialog, text="Товар:").pack(pady=10)
        product_combo = ttk.Combobox(dialog, values=[f"{p['name']} ({p['quantity']} шт.)" for p in products], width=35)
        product_combo.pack(pady=5)
        
        tk.Label(dialog, text="Количество:").pack(pady=5)
        quantity_entry = tk.Entry(dialog, width=30)
        quantity_entry.pack(pady=5)
        
        def save():
            selected = product_combo.get()
            product_name = selected.split(' (')[0]
            product = None
            for p in products:
                if p['name'] == product_name:
                    product = p
                    break
            
            if product:
                try:
                    qty = int(quantity_entry.get())
                    if self.order_detail_model.add(oid, product['id'], qty, product['price']):
                        dialog.destroy()
                        self.load_orders()
                        self.load_order_details(None)
                    else:
                        messagebox.showerror("Ошибка", "Недостаточно товара на складе")
                except:
                    messagebox.showerror("Ошибка", "Введите корректное количество")
        
        tk.Button(dialog, text="Добавить", command=save).pack(pady=20)

    def remove_order_item(self):
        if self.user_role not in ['Администратор', 'Менеджер']:
            messagebox.showerror("Ошибка", "У вас нет прав на удаление товаров из заказа")
            return
    
        sel_order = self.orders_tree.selection()
        if not sel_order:
            messagebox.showwarning("Внимание", "Сначала выберите заказ")
            return
    
        sel_item = self.detail_tree.selection()
        if not sel_item:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
    
        order_id = self.orders_tree.item(sel_order[0])['values'][0]
        status = self.orders_tree.item(sel_order[0])['values'][4]
    
        if status in ['Отправлен', 'Доставлен', 'Отменён']:
            messagebox.showwarning("Внимание", f"Нельзя удалять товары из заказа со статусом '{status}'")
            return
    
        item_values = self.detail_tree.item(sel_item[0])['values']
        detail_id = item_values[0]
        product_name = item_values[1]
        quantity = item_values[2]
        price = item_values[3]
    
        if not messagebox.askyesno("Подтверждение", f"Удалить товар '{product_name}' (кол-во: {quantity}) из заказа?"):
            return
    
        if self.order_detail_model.remove_item(detail_id, order_id, product_name, quantity):
            self.load_orders()
            self.load_order_details(None)
            messagebox.showinfo("Успех", "Товар удалён из заказа")
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить товар")
    
    def change_order_status(self):
        if self.user_role not in ['Администратор', 'Менеджер']:
            messagebox.showerror("Ошибка", "У вас нет прав на изменение статуса заказов")
            return

        sel = self.orders_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        
        oid = self.orders_tree.item(sel[0])['values'][0]
        cur_status = self.orders_tree.item(sel[0])['values'][4]
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Изменить статус заказа")
        dialog.geometry("300x150")
        dialog.grab_set()
        
        statuses = ['Новый', 'Обработан', 'Отправлен', 'Доставлен', 'Отменён']
        
        tk.Label(dialog, text="Новый статус:").pack(pady=10)
        status_combo = ttk.Combobox(dialog, values=statuses, width=20)
        status_combo.set(cur_status)
        status_combo.pack(pady=5)
        
        def save():
            new_status = status_combo.get()
            self.order_model.update_status(oid, new_status)
            dialog.destroy()
            self.load_orders()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def refresh(self):
        self.load_orders()