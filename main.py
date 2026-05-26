import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from gui import MainApp


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация - Строительный магазин")
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 600
        height = 400
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        title_label = tk.Label(
            self.root, 
            text="Строительный магазин", 
            font=('Arial', 18, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(
            self.root,
            text="Вход в систему",
            font=('Arial', 12),
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 20))
        
        frame = ttk.Frame(self.root, padding="30")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Логин:", font=('Arial', 10)).pack(anchor='w', pady=(0, 5))
        self.username_entry = ttk.Entry(frame, font=('Arial', 11), width=30)
        self.username_entry.pack(fill='x', pady=(0, 15))
        
        ttk.Label(frame, text="Пароль:", font=('Arial', 10)).pack(anchor='w', pady=(0, 5))
        self.password_entry = ttk.Entry(frame, font=('Arial', 11), width=30, show="*")
        self.password_entry.pack(fill='x', pady=(0, 20))
        
        login_btn = ttk.Button(frame, text="Войти", command=self.login, width=20)
        login_btn.pack(pady=10)
        
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return
        
        try:
            conn = sqlite3.connect('shop.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, full_name, role 
                FROM Users 
                WHERE username = ? AND password = ? AND is_active = 1
            """, (username, password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_info = {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
                
                self.root.destroy()
                
                root_main = tk.Tk()
                app = MainApp(root_main, user_info)
                root_main.mainloop()
                
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
                self.password_entry.delete(0, tk.END)
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось подключиться к БД:\n{str(e)}")


def main():
    from database import init_db
    init_db()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
    from models import ProductModel, CategoryModel

    cat_model = CategoryModel()
    prod_model = ProductModel()


if __name__ == "__main__":
    main()