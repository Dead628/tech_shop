import tkinter as tk
from tkinter import ttk, messagebox
from models import CustomerModel


class CustomersTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.customer_model = CustomerModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Клиенты")
        
        self.create_widgets()
        self.load_customers()
    
    def create_widgets(self):
        cols = ('ID', 'ФИО', 'Телефон', 'Email')
        self.tree = ttk.Treeview(self.tab, columns=cols, show='headings', height=20)
        col_widths = [50, 250, 150, 250]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        bf = ttk.Frame(self.tab)
        bf.pack(pady=10)
        ttk.Button(bf, text="Добавить", command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(bf, text="Редактировать", command=self.edit_customer).pack(side='left', padx=5)
        ttk.Button(bf, text="Удалить", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_customers).pack(side='left', padx=5)
    
    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for c in self.customer_model.get_all():
            self.tree.insert('', 'end', values=(
                c['id'], c['name'], c['phone'] or '', c['email'] or ''
            ))
    
    def add_customer(self):
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить клиента")
        dialog.geometry("400x350")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="ФИО:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Телефон:").pack(pady=5)
        entries['phone'] = tk.Entry(dialog, width=40)
        entries['phone'].pack(pady=5)
        
        tk.Label(dialog, text="Email:").pack(pady=5)
        entries['email'] = tk.Entry(dialog, width=40)
        entries['email'].pack(pady=5)
        
        def save():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip() or None
            email = entries['email'].get().strip() or None
            
            if not name:
                messagebox.showerror("Ошибка", "Введите ФИО")
                return
            if not phone and not email:
                messagebox.showerror("Ошибка", "Заполните телефон или email")
                return
            
            self.customer_model.add(name, phone, email)
            dialog.destroy()
            self.load_customers()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_customer(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return
        
        cid = self.tree.item(sel[0])['values'][0]
        c = self.customer_model.get_by_id(cid)
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать клиента")
        dialog.geometry("400x350")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="ФИО:").pack(pady=5)
        entries['name'] = tk.Entry(dialog, width=40)
        entries['name'].insert(0, c['name'])
        entries['name'].pack(pady=5)
        
        tk.Label(dialog, text="Телефон:").pack(pady=5)
        entries['phone'] = tk.Entry(dialog, width=40)
        entries['phone'].insert(0, c['phone'] or '')
        entries['phone'].pack(pady=5)
        
        tk.Label(dialog, text="Email:").pack(pady=5)
        entries['email'] = tk.Entry(dialog, width=40)
        entries['email'].insert(0, c['email'] or '')
        entries['email'].pack(pady=5)
        
        def save():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip() or None
            email = entries['email'].get().strip() or None
            
            if not name:
                messagebox.showerror("Ошибка", "Введите ФИО")
                return
            if not phone and not email:
                messagebox.showerror("Ошибка", "Заполните телефон или email")
                return
            
            self.customer_model.update(cid, name, phone, email)
            dialog.destroy()
            self.load_customers()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_customer(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            cid = self.tree.item(sel[0])['values'][0]
            self.customer_model.delete(cid)
            self.load_customers()

    
    def refresh(self):
        self.load_customers()