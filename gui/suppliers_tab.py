import tkinter as tk
from tkinter import ttk, messagebox
from models import SupplierModel


class SuppliersTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.supplier_model = SupplierModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Поставщики")
        
        self.create_widgets()
        self.load_suppliers()
    
    def create_widgets(self):
        cols = ('ID', 'Название', 'Телефон', 'Email', 'Адрес')
        self.tree = ttk.Treeview(self.tab, columns=cols, show='headings', height=20)
        col_widths = [50, 200, 150, 200, 250]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        bf = ttk.Frame(self.tab)
        bf.pack(pady=10)
        ttk.Button(bf, text="Добавить", command=self.add_supplier).pack(side='left', padx=5)
        ttk.Button(bf, text="Редактировать", command=self.edit_supplier).pack(side='left', padx=5)
        ttk.Button(bf, text="Удалить", command=self.delete_supplier).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_suppliers).pack(side='left', padx=5)
    
    def load_suppliers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for s in self.supplier_model.get_all():
            self.tree.insert('', 'end', values=(
                s['id'], s['name'], s['phone'] or '', s['email'] or '', s['address'] or ''
            ))
    
    def add_supplier(self):
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить поставщика")
        dialog.geometry("400x400")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Телефон:").pack(pady=5)
        entries['phone'] = tk.Entry(dialog, width=40)
        entries['phone'].pack(pady=5)
        
        tk.Label(dialog, text="Email:").pack(pady=5)
        entries['email'] = tk.Entry(dialog, width=40)
        entries['email'].pack(pady=5)
        
        tk.Label(dialog, text="Адрес:").pack(pady=5)
        entries['address'] = tk.Entry(dialog, width=40)
        entries['address'].pack(pady=5)
        
        def save():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip() or None
            email = entries['email'].get().strip() or None
            address = entries['address'].get().strip() or None
            
            if not name:
                messagebox.showerror("Ошибка", "Введите название")
                return
            if not phone and not email:
                messagebox.showerror("Ошибка", "Заполните телефон или email")
                return
            
            self.supplier_model.add(name, phone, email, address)
            dialog.destroy()
            self.load_suppliers()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_supplier(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите поставщика")
            return
        
        sid = self.tree.item(sel[0])['values'][0]
        s = self.supplier_model.get_by_id(sid)
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать поставщика")
        dialog.geometry("400x400")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].insert(0, s['name'])
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Телефон:").pack(pady=5)
        entries['phone'] = tk.Entry(dialog, width=40)
        entries['phone'].insert(0, s['phone'] or '')
        entries['phone'].pack(pady=5)
        
        tk.Label(dialog, text="Email:").pack(pady=5)
        entries['email'] = tk.Entry(dialog, width=40)
        entries['email'].insert(0, s['email'] or '')
        entries['email'].pack(pady=5)
        
        tk.Label(dialog, text="Адрес:").pack(pady=5)
        entries['address'] = tk.Entry(dialog, width=40)
        entries['address'].insert(0, s['address'] or '')
        entries['address'].pack(pady=5)
        
        def save():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip() or None
            email = entries['email'].get().strip() or None
            address = entries['address'].get().strip() or None
            
            if not name:
                messagebox.showerror("Ошибка", "Введите название")
                return
            if not phone and not email:
                messagebox.showerror("Ошибка", "Заполните телефон или email")
                return
            
            self.supplier_model.update(sid, name, phone, email, address)
            dialog.destroy()
            self.load_suppliers()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_supplier(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите поставщика")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить поставщика?"):
            sid = self.tree.item(sel[0])['values'][0]
            self.supplier_model.delete(sid)
            self.load_suppliers()
    
    def refresh(self):
        self.load_suppliers()