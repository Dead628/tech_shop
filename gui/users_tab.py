import tkinter as tk
from tkinter import ttk, messagebox
from models import UserModel


class UsersTab:
    def __init__(self, notebook, user_role):
        self.user_role = user_role
        self.user_model = UserModel()
        
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Пользователи")
        
        self.create_widgets()
        self.load_users()
    
    def create_widgets(self):
        cols = ('ID', 'Логин', 'ФИО', 'Роль', 'Активен')
        self.tree = ttk.Treeview(self.tab, columns=cols, show='headings', height=20)
        col_widths = [50, 150, 200, 150, 80]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        bf = ttk.Frame(self.tab)
        bf.pack(pady=10)
        ttk.Button(bf, text="Добавить", command=self.add_user).pack(side='left', padx=5)
        ttk.Button(bf, text="Редактировать", command=self.edit_user).pack(side='left', padx=5)
        ttk.Button(bf, text="Удалить", command=self.delete_user).pack(side='left', padx=5)
        ttk.Button(bf, text="Обновить", command=self.load_users).pack(side='left', padx=5)
    
    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for u in self.user_model.get_all():
            active = "Да" if u.get('is_active', 1) else "Нет"
            self.tree.insert('', 'end', values=(
                u['id'], u['username'], u['full_name'], u['role'], active
            ))
    
    def add_user(self):
        dialog = tk.Toplevel(self.tab)
        dialog.title("Добавить пользователя")
        dialog.geometry("400x450")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Логин:").pack(pady=5)
        entries['username'] = tk.Entry(dialog, width=40)
        entries['username'].pack(pady=5)
        
        tk.Label(dialog, text="Пароль:").pack(pady=5)
        entries['password'] = tk.Entry(dialog, width=40, show="*")
        entries['password'].pack(pady=5)
        
        tk.Label(dialog, text="ФИО:").pack(pady=5)
        entries['full_name'] = tk.Entry(dialog, width=40)
        entries['full_name'].pack(pady=5)
        
        tk.Label(dialog, text="Роль:").pack(pady=5)
        roles = ['Администратор', 'Менеджер', 'Кассир-кладовщик']
        entries['role'] = ttk.Combobox(dialog, values=roles, width=37)
        entries['role'].pack(pady=5)
        
        tk.Label(dialog, text="Активен:").pack(pady=5)
        entries['is_active'] = tk.IntVar(value=1)
        ttk.Checkbutton(dialog, text="Да", variable=entries['is_active']).pack(pady=5)
        
        def save():
            username = entries['username'].get().strip()
            password = entries['password'].get()
            full_name = entries['full_name'].get().strip()
            role = entries['role'].get()
            is_active = entries['is_active'].get()
            
            if not username or not password or not full_name or not role:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            self.user_model.add(username, password, full_name, role, is_active)
            dialog.destroy()
            self.load_users()
            messagebox.showinfo("Успех", "Пользователь добавлен")
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return
        
        uid = self.tree.item(sel[0])['values'][0]
        u = self.user_model.get_by_id(uid)
        
        dialog = tk.Toplevel(self.tab)
        dialog.title("Редактировать пользователя")
        dialog.geometry("400x480")
        dialog.grab_set()
        
        entries = {}
        
        tk.Label(dialog, text="Логин:").pack(pady=5)
        entries['username'] = tk.Entry(dialog, width=40)
        entries['username'].insert(0, u['username'])
        entries['username'].pack(pady=5)
        
        tk.Label(dialog, text="Новый пароль (оставьте пустым):").pack(pady=5)
        entries['password'] = tk.Entry(dialog, width=40, show="*")
        entries['password'].pack(pady=5)
        
        tk.Label(dialog, text="ФИО:").pack(pady=5)
        entries['full_name'] = tk.Entry(dialog, width=40)
        entries['full_name'].insert(0, u['full_name'])
        entries['full_name'].pack(pady=5)
        
        tk.Label(dialog, text="Роль:").pack(pady=5)
        roles = ['Администратор', 'Менеджер', 'Кассир-кладовщик']
        entries['role'] = ttk.Combobox(dialog, values=roles, width=37)
        entries['role'].set(u['role'])
        entries['role'].pack(pady=5)
        
        tk.Label(dialog, text="Активен:").pack(pady=5)
        entries['is_active'] = tk.IntVar(value=u.get('is_active', 1))
        ttk.Checkbutton(dialog, text="Да", variable=entries['is_active']).pack(pady=5)
        
        def save():
            username = entries['username'].get().strip()
            full_name = entries['full_name'].get().strip()
            role = entries['role'].get()
            is_active = entries['is_active'].get()
            
            if not username or not full_name or not role:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            if entries['password'].get():
                self.user_model.change_password(uid, entries['password'].get())
            
            self.user_model.update(uid, username, full_name, role, is_active)
            dialog.destroy()
            self.load_users()
            messagebox.showinfo("Успех", "Пользователь обновлён")
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить пользователя?"):
            uid = self.tree.item(sel[0])['values'][0]
            self.user_model.delete(uid)
            self.load_users()
            messagebox.showinfo("Успех", "Пользователь удалён")
    
    def refresh(self):
        self.load_users()