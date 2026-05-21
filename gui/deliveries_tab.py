import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import DeliveryModel, DeliveryDetailModel, SupplierModel, ProductModel


class DeliveriesTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.delivery_model = DeliveryModel()
        self.delivery_detail_model = DeliveryDetailModel()
        self.supplier_model = SupplierModel()
        self.product_model = ProductModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Поставки")
        
        self.create_widgets()
        self.load_deliveries()
    
    def create_widgets(self):
        top = ttk.Frame(self.tab)
        top.pack(fill='both', expand=True)
        
        cols = ('ID', 'Поставщик', 'Дата и время', 'Сумма', 'Статус')
        self.deliveries_tree = ttk.Treeview(top, columns=cols, show='headings', height=10)
        col_widths = [50, 200, 180, 120, 150]
        for col, w in zip(cols, col_widths):
            self.deliveries_tree.heading(col, text=col)
            self.deliveries_tree.column(col, width=w)
        self.deliveries_tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        bf = ttk.Frame(top)
        bf.pack(pady=5)
        ttk.Button(bf, text="Новая поставка", command=self.create_delivery).pack(side='left', padx=5)
        ttk.Button(bf, text="Изменить статус", command=self.change_delivery_status).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_deliveries).pack(side='left', padx=5)
        
        bottom = ttk.LabelFrame(self.tab, text="Детали поставки")
        bottom.pack(fill='both', expand=True)
        
        detail_cols = ('ID', 'Товар', 'Количество', 'Цена за единицу', 'Сумма')
        self.detail_tree = ttk.Treeview(bottom, columns=detail_cols, show='headings', height=8)
        detail_widths = [50, 250, 100, 120, 120]
        for col, w in zip(detail_cols, detail_widths):
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=w)
        self.detail_tree.pack(fill='both', expand=True, padx=10, pady=5)
        btn_frame = ttk.Frame(bottom)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Добавить товар", command=self.add_delivery_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить товар", command=self.remove_delivery_item).pack(side='left', padx=5)
        
        self.deliveries_tree.bind('<<TreeviewSelect>>', self.load_delivery_details)
    
    def load_deliveries(self):
        for item in self.deliveries_tree.get_children():
            self.deliveries_tree.delete(item)
        
        for d in self.delivery_model.get_all():
            s = self.supplier_model.get_by_id(d['supplier_id'])
            self.deliveries_tree.insert('', 'end', values=(
                d['id'], s['name'] if s else 'Нет', d['delivery_datetime'], d['total_amount'], d['status']
            ))
    
    def load_delivery_details(self, event):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        sel = self.deliveries_tree.selection()
        if not sel:
            return
        
        did = self.deliveries_tree.item(sel[0])['values'][0]
        for d in self.delivery_detail_model.get_by_delivery(did):
            self.detail_tree.insert('', 'end', values=(
                d['id'], d['product_name'], d['quantity'], d['price_per_unit'],
                d['quantity'] * d['price_per_unit']
            ))
    
    def create_delivery(self):
        if self.user_role not in ['Администратор', 'Кассир-кладовщик']:
            messagebox.showerror("Ошибка", "У вас нет прав на создание поставок")
            return
        suppliers = self.supplier_model.get_all()
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Новая поставка")
        dialog.geometry("400x250")
        dialog.grab_set()
        
        tk.Label(dialog, text="Поставщик:").pack(pady=10)
        supplier_combo = ttk.Combobox(dialog, values=[s['name'] for s in suppliers], width=30)
        supplier_combo.pack(pady=5)
        
        tk.Label(dialog, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ:СС):").pack(pady=5)
        date_entry = tk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        date_entry.pack(pady=5)
        
        def save():
            selected = supplier_combo.get()
            for s in suppliers:
                if s['name'] == selected:
                    self.delivery_model.add(s['id'], date_entry.get())
                    break
            dialog.destroy()
            self.load_deliveries()
        
        tk.Button(dialog, text="Создать", command=save).pack(pady=20)
    
    def add_delivery_item(self):
        if self.user_role not in ['Администратор', 'Кассир-кладовщик']:
            messagebox.showerror("Ошибка", "У вас нет прав на создание поставок")
        sel = self.deliveries_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Сначала выберите поставку")
            return
        
        did = self.deliveries_tree.item(sel[0])['values'][0]
        products = self.product_model.get_all()
        status = self.deliveries_tree.item(sel[0])['values'][4]
    
        if status in ['Завершена', 'Отменена']:
            messagebox.showwarning("Внимание", f"Нельзя добавлять товары в поставку со статусом '{status}'")
            return
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить товар в поставку")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        tk.Label(dialog, text="Товар:").pack(pady=10)
        product_combo = ttk.Combobox(dialog, values=[p['name'] for p in products], width=35)
        product_combo.pack(pady=5)
        
        tk.Label(dialog, text="Количество:").pack(pady=5)
        quantity_entry = tk.Entry(dialog, width=30)
        quantity_entry.pack(pady=5)
        
        tk.Label(dialog, text="Цена за единицу:").pack(pady=5)
        price_entry = tk.Entry(dialog, width=30)
        price_entry.pack(pady=5)
        
        def save():
            selected = product_combo.get()
            product = None
            for p in products:
                if p['name'] == selected:
                    product = p
                    break
            
            if product:
                try:
                    qty = int(quantity_entry.get())
                    price = float(price_entry.get())
                    self.delivery_detail_model.add(did, product['id'], qty, price)
                    dialog.destroy()
                    self.load_deliveries()
                    self.load_delivery_details(None)
                    messagebox.showinfo("Успех", "Товар добавлен в поставку")
                except:
                    messagebox.showerror("Ошибка", "Введите корректные данные")
        
        tk.Button(dialog, text="Добавить", command=save).pack(pady=20)

    def remove_delivery_item(self):
        if self.user_role not in ['Администратор', 'Кассир-кладовщик']:
            messagebox.showerror("Ошибка", "У вас нет прав на удаление товаров из поставки")
            return
    
        sel_delivery = self.deliveries_tree.selection()
        if not sel_delivery:
            messagebox.showwarning("Внимание", "Сначала выберите поставку")
            return
    
        sel_item = self.detail_tree.selection()
        if not sel_item:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
    
        delivery_id = self.deliveries_tree.item(sel_delivery[0])['values'][0]
        status = self.deliveries_tree.item(sel_delivery[0])['values'][4]
    
        if status in ['Завершена', 'Отменена']:
            messagebox.showwarning("Внимание", f"Нельзя удалять товары из поставки со статусом '{status}'")
            return
    
        item_values = self.detail_tree.item(sel_item[0])['values']
        detail_id = item_values[0]
        product_name = item_values[1]
        quantity = item_values[2]
    
        if not messagebox.askyesno("Подтверждение", f"Удалить товар '{product_name}' (кол-во: {quantity}) из поставки?"):
            return
    
        if self.delivery_detail_model.remove_item(detail_id, delivery_id, product_name, quantity):
            self.load_deliveries()
            self.load_delivery_details(None)
            messagebox.showinfo("Успех", "Товар удалён из поставки")
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить товар")
    
    def change_delivery_status(self):
        if self.user_role not in ['Администратор', 'Кассир-кладовщик']:
            messagebox.showerror("Ошибка", "У вас нет прав на изменение статуса поставок")
            return
        sel = self.deliveries_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите поставку")
            return
        
        did = self.deliveries_tree.item(sel[0])['values'][0]
        cur_status = self.deliveries_tree.item(sel[0])['values'][4]
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Изменить статус поставки")
        dialog.geometry("300x150")
        dialog.grab_set()
        
        statuses = ['Ожидается', 'В пути', 'Завершена', 'Отменена']
        
        tk.Label(dialog, text="Новый статус:").pack(pady=10)
        status_combo = ttk.Combobox(dialog, values=statuses, width=20)
        status_combo.set(cur_status)
        status_combo.pack(pady=5)
        
        def save():
            new_status = status_combo.get()
            self.delivery_model.update_status(did, new_status)
            dialog.destroy()
            self.load_deliveries()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def refresh(self):
        self.load_deliveries()