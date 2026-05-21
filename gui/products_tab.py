import tkinter as tk
from tkinter import ttk, messagebox
from models import ProductModel, CategoryModel, SupplierModel


class ProductsTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.product_model = ProductModel()
        self.category_model = CategoryModel()
        self.supplier_model = SupplierModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Товары")
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        f = ttk.Frame(self.tab)
        f.pack(pady=5, fill='x')
        ttk.Label(f, text="Поиск:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(f, width=30)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(f, text="Найти", command=self.search_products).pack(side='left', padx=2)
        ttk.Button(f, text="Сброс", command=self.load_products).pack(side='left', padx=2)
        
        cols = ('ID', 'Название', 'Цена', 'Количество', 'Категория', 'Поставщик')
        self.tree = ttk.Treeview(self.tab, columns=cols, show='headings', height=20)
        col_widths = [50, 250, 100, 100, 150, 150]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        bf = ttk.Frame(self.tab)
        bf.pack(pady=10)
        ttk.Button(bf, text="Добавить", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(bf, text="Редактировать", command=self.edit_product).pack(side='left', padx=5)
        ttk.Button(bf, text="Удалить", command=self.delete_product).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_products).pack(side='left', padx=5)
    
    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for p in self.product_model.get_all():
            cat = self.category_model.get_by_id(p['category_id'])
            sup = self.supplier_model.get_by_id(p['supplier_id']) if p['supplier_id'] else None
            self.tree.insert('', 'end', values=(
                p['id'], p['name'], p['price'], p['quantity'],
                cat['name'] if cat else 'Нет',
                sup['name'] if sup else 'Нет'
            ))
    
    def search_products(self):
        kw = self.search_entry.get().strip()
        if not kw:
            self.load_products()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for p in self.product_model.search(kw):
            cat = self.category_model.get_by_id(p['category_id'])
            sup = self.supplier_model.get_by_id(p['supplier_id']) if p['supplier_id'] else None
            self.tree.insert('', 'end', values=(
                p['id'], p['name'], p['price'], p['quantity'],
                cat['name'] if cat else 'Нет',
                sup['name'] if sup else 'Нет'
            ))
    
    def add_product(self):
        cats = self.category_model.get_all()
        sups = self.supplier_model.get_all()
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить товар")
        dialog.geometry("400x450")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Цена:").pack(pady=5)
        entries['price'] = tk.Entry(dialog, width=40)
        entries['price'].pack(pady=5)
        
        tk.Label(dialog, text="Количество:").pack(pady=5)
        entries['quantity'] = tk.Entry(dialog, width=40)
        entries['quantity'].pack(pady=5)
        
        tk.Label(dialog, text="Категория:").pack(pady=5)
        entries['category'] = ttk.Combobox(dialog, values=[c['name'] for c in cats], width=37)
        entries['category'].pack(pady=5)
        
        tk.Label(dialog, text="Поставщик:").pack(pady=5)
        entries['supplier'] = ttk.Combobox(dialog, values=[s['name'] for s in sups], width=37)
        entries['supplier'].pack(pady=5)
        
        def save():
            try:
                name = entries['name'].get().strip()
                price = float(entries['price'].get())
                quantity = int(entries['quantity'].get())
                
                if not name:
                    messagebox.showerror("Ошибка", "Введите название")
                    return
                
                cat_id = None
                for c in cats:
                    if c['name'] == entries['category'].get():
                        cat_id = c['id']
                        break
                
                sup_id = None
                if entries['supplier'].get():
                    for s in sups:
                        if s['name'] == entries['supplier'].get():
                            sup_id = s['id']
                            break
                
                self.product_model.add(name, price, quantity, cat_id, sup_id)
                dialog.destroy()
                self.load_products()
            except:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода")
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        
        pid = self.tree.item(sel[0])['values'][0]
        p = self.product_model.get_by_id(pid)
        cats = self.category_model.get_all()
        sups = self.supplier_model.get_all()
        
        cat = self.category_model.get_by_id(p['category_id'])
        sup = self.supplier_model.get_by_id(p['supplier_id']) if p['supplier_id'] else None
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать товар")
        dialog.geometry("400x450")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].insert(0, p['name'])
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Цена:").pack(pady=5)
        entries['price'] = tk.Entry(dialog, width=40)
        entries['price'].insert(0, str(p['price']))
        entries['price'].pack(pady=5)
        
        tk.Label(dialog, text="Количество:").pack(pady=5)
        entries['quantity'] = tk.Entry(dialog, width=40)
        entries['quantity'].insert(0, str(p['quantity']))
        entries['quantity'].pack(pady=5)
        
        tk.Label(dialog, text="Категория:").pack(pady=5)
        entries['category'] = ttk.Combobox(dialog, values=[c['name'] for c in cats], width=37)
        if cat:
            entries['category'].set(cat['name'])
        entries['category'].pack(pady=5)
        
        tk.Label(dialog, text="Поставщик:").pack(pady=5)
        entries['supplier'] = ttk.Combobox(dialog, values=[s['name'] for s in sups], width=37)
        if sup:
            entries['supplier'].set(sup['name'])
        entries['supplier'].pack(pady=5)
        
        def save():
            try:
                name = entries['name'].get().strip()
                price = float(entries['price'].get())
                quantity = int(entries['quantity'].get())
                
                cat_id = None
                for c in cats:
                    if c['name'] == entries['category'].get():
                        cat_id = c['id']
                        break
                
                sup_id = None
                if entries['supplier'].get():
                    for s in sups:
                        if s['name'] == entries['supplier'].get():
                            sup_id = s['id']
                            break
                
                self.product_model.update(pid, name, price, quantity, cat_id, sup_id)
                dialog.destroy()
                self.load_products()
            except:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода")
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить товар?"):
            pid = self.tree.item(sel[0])['values'][0]
            self.product_model.delete(pid)
            self.load_products()
    
    def refresh(self):
        self.load_products()
    def clear_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)