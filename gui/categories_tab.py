import tkinter as tk
from tkinter import ttk, messagebox
from models import CategoryModel


class CategoriesTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.category_model = CategoryModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Категории")
        
        self.create_widgets()
        self.load_categories()
    
    def create_widgets(self):
        cols = ('ID', 'Название', 'Описание')
        self.tree = ttk.Treeview(self.tab, columns=cols, show='headings', height=20)
        col_widths = [50, 250, 500]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        bf = ttk.Frame(self.tab)
        bf.pack(pady=10)
        
        if self.user_role == 'Администратор':
            ttk.Button(bf, text="Добавить", command=self.add_category).pack(side='left', padx=5)
            ttk.Button(bf, text="Редактировать", command=self.edit_category).pack(side='left', padx=5)
            ttk.Button(bf, text="Удалить", command=self.delete_category).pack(side='left', padx=5)
        
        ttk.Button(bf, text="Обновить", command=self.load_categories).pack(side='left', padx=5)
    
    def load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for c in self.category_model.get_all():
            self.tree.insert('', 'end', values=(c['id'], c['name'], c['description'] or ''))
    
    def add_category(self):
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить категорию")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Описание:").pack(pady=5)
        desc_text = tk.Text(dialog, height=5, width=40)
        desc_text.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название")
                return
            desc = desc_text.get("1.0", tk.END).strip()
            self.category_model.add(name, desc)
            dialog.destroy()
            self.load_categories()

        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_category(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите категорию")
            return
        
        cid = self.tree.item(sel[0])['values'][0]
        c = self.category_model.get_by_id(cid)
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать категорию")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        tk.Label(dialog, text="Название:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, c['name'])
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Описание:").pack(pady=5)
        desc_text = tk.Text(dialog, height=5, width=40)
        if c['description']:
            desc_text.insert("1.0", c['description'])
        desc_text.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название")
                return
            desc = desc_text.get("1.0", tk.END).strip()
            self.category_model.update(cid, name, desc)
            dialog.destroy()
            self.load_categories()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_category(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите категорию")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить категорию?"):
            cid = self.tree.item(sel[0])['values'][0]
            self.category_model.delete(cid)
            self.load_categories()
    
    def refresh(self):
        self.load_categories()
    
    def clear_data(self):
        """Очистка данных (вызывается из главного окна)"""
        for item in self.tree.get_children():
            self.tree.delete(item)