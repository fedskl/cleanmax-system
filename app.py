import customtkinter
import tkinter
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
from pathlib import Path
import sqlite3
import os
import bcrypt

from data import DataBase
from pages import Pages
from database_functions import DatabaseFunctions
from windows import Windows

class CleanMax(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("CleanMax")
        x = (self.winfo_screenwidth() // 2) - (1280 // 2)
        y = (self.winfo_screenheight() // 2) - (720 // 2)
        self.geometry(f"1280x720+{x}+{y}")
        self.resizable(False, False)
        self.configure(fg_color="#E5E9F2")
        self.ICONS_PATH = Path(__file__).parent / "icons"
        ico_path = os.path.abspath(self.ICONS_PATH / "washer.ico")
        self.iconbitmap(ico_path)
        self.con_database = DataBase()
        
        self.pages = Pages(self)
        self.db_functions = DatabaseFunctions(self)
        self.windows = Windows(self)
        
        self.create_widgets()
        self.windows.window_login()
        self.mainloop()

    def create_widgets(self):
        self.create_sidebar()
        self.create_header()

        self.main_area = customtkinter.CTkFrame(self, fg_color="#E5E9F2")
        self.main_area.pack(fill=tkinter.BOTH, expand=True)

    def create_sidebar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, height=400)
        self.sidebar_frame.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.sidebar_frame.configure(fg_color="#708090", 
                                    bg_color="#708090",
                                    width=200,
                                    height=400)
        
        self.create_sidebar_content()

    def create_sidebar_content(self):
        self.content_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.content_frame.pack(expand=True)

        button_style = {
            "master": self.content_frame,
            "fg_color": "#4FA3C7",
            "hover_color": "#3A90B4",
            "text_color": "#FFFFFF",
            "corner_radius": 0,
            "height": 40,
            "width": 200,
            "font": ("Mohave", 16, "bold")
        }

        home_icon = self.create_image_button(self.ICONS_PATH / "home.png")
        clientes_icon = self.create_image_button(self.ICONS_PATH / "clientes.png")
        new_cliente_icon = self.create_image_button(self.ICONS_PATH / "new_cliente.png")
        settings_icon = self.create_image_button(self.ICONS_PATH / "settings.png")
        reports_icon = self.create_image_button(self.ICONS_PATH / "reports.png")
        exit_icon = self.create_image_button(self.ICONS_PATH / "exit.png")

        self.home_btn = customtkinter.CTkButton(**button_style, text="Home", image=home_icon, command=self.pages.show_home_page)
        self.home_btn.pack(fill=tkinter.X, pady=5, padx=0)
        
        self.clientes_btn = customtkinter.CTkButton(**button_style, text="Clientes", image=clientes_icon, command=self.pages.show_clientes_page)
        self.clientes_btn.pack(fill=tkinter.X, pady=5, padx=0)
        
        self.new_cliente_btn = customtkinter.CTkButton(**button_style, text="Novo Cliente", image=new_cliente_icon, command=self.pages.show_new_cliente_page)
        self.new_cliente_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.reports_btn = customtkinter.CTkButton(**button_style, text="Relatórios", image=reports_icon, command=self.pages.show_reports_page)
        self.reports_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.settings_btn = customtkinter.CTkButton(**button_style, text="Configurações", image=settings_icon, command=self.pages.show_settings_page)
        self.settings_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.exit_btn = customtkinter.CTkButton(**button_style, text="Sair", image=exit_icon, command=self.exit_app)
        self.exit_btn.pack(fill=tkinter.X, pady=5, padx=0)

    def create_header(self):
        self.header_frame = customtkinter.CTkFrame(self, width=1200, height=100)
        self.header_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        self.header_frame.configure(fg_color="#5A7684", 
                                    bg_color="#5A7684",
                                    width=1200,
                                    height=100)
        
        self.create_header_content()

    def create_header_content(self):
        self.title_label = customtkinter.CTkLabel(
            self.header_frame,
            text="CleanMax - Sistema de Gestão",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.title_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        
        image = Image.open(self.ICONS_PATH / "logout.png")
        icon_image = customtkinter.CTkImage(light_image=image, dark_image=image, size=(36, 36))
        self.logout_btn = customtkinter.CTkButton(
            self.header_frame,
            text="",
            image=icon_image,
            width=50,
            fg_color="transparent",
            hover_color="#F9FAFB",
            command=self.logout
        )
        self.logout_btn.place(relx=0.93, rely=0.5, anchor=tkinter.W)

    def exit_app(self):
        self.destroy()

    def logout(self):
        self.withdraw()
        self.windows.window_login()

    def show_main_window(self):
        self.deiconify()
        if hasattr(self, 'login_window'):
            self.login_window.destroy()

    def create_image_button(self, image_path):
        image = Image.open(image_path)
        return customtkinter.CTkImage(light_image=image, dark_image=image, size=(24, 24))

    def reset_button_styles(self):
        button_style = {
            "fg_color": "#4FA3C7",
            "hover_color": "#3A90B4",
            "text_color": "#FFFFFF",
            "corner_radius": 0,
            "height": 40,
            "font": ("Mohave", 16, "bold")
        }
        
        self.home_btn.configure(**button_style)
        self.clientes_btn.configure(**button_style)
        self.new_cliente_btn.configure(**button_style)
        self.settings_btn.configure(**button_style)
        self.reports_btn.configure(**button_style)
        
    def clear_content(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def autentic(self, tablenome):
        try:
            username = self.username_Entry.get().strip()
            password = self.password_Entry.get().strip()

            if not username or not password:
                messagebox.showerror(title="Erro", message="Por favor, preencha todos os campos.")
                return

            tabelas_validas = ['users', 'admin_users']
            if tablenome not in tabelas_validas:
                messagebox.showerror("Erro", "Tabela inválida!")
                return

            query = "SELECT id, name, password FROM users WHERE name = ?"
            self.con_database.cur.execute(query, (username,))
            user_data = self.con_database.cur.fetchone()

            if user_data:
                user_id, user_name, senha_hash_armazenada = user_data
                
                if isinstance(senha_hash_armazenada, bytes) or (isinstance(senha_hash_armazenada, str) and senha_hash_armazenada.startswith('$2b$')):
                    if bcrypt.checkpw(password.encode('utf-8'), senha_hash_armazenada):
                        self.deiconify()          
                        self.login_window.destroy()
                    else:
                        messagebox.showerror("Acesso inválido", "Usuário ou senha inválidos.")
                else:
                    if password == senha_hash_armazenada:
                        salt = bcrypt.gensalt()
                        novo_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
                        
                        self.con_database.cur.execute(
                            "UPDATE users SET password = ? WHERE id = ?",
                            (novo_hash, user_id)
                        )
                        self.con_database.dbase.commit()
                        
                        self.deiconify()          
                        self.login_window.destroy()
                    else:
                        messagebox.showerror("Acesso inválido", "Usuário ou senha inválidos.")
            else:
                messagebox.showerror("Acesso inválido", "Usuário ou senha inválidos.")
                
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao autenticar: {ex}")