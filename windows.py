import customtkinter
import tkinter
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
import datetime
from tkinter import filedialog
import shutil
from pathlib import Path
from data import DataBase
import os

class Windows:
    def __init__(self, app):
        self.app = app

    def window_login(self):
        self.app.login_window = customtkinter.CTkToplevel(self.app)
        self.app.login_window.title("Login - CleanMax")
        self.app.login_window.geometry("300x500")
        self.app.login_window.resizable(False, False)
        self.app.login_window.transient(self.app)
        self.app.login_window.grab_set()
        self.app.login_window.focus_force()
        self.app.login_window.configure(fg_color="#E5E9F2")
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        self.app.login_window.iconbitmap(ico_path)
        
        self.app.left_frame = customtkinter.CTkFrame(self.app.login_window, bg_color="#5A7684", fg_color="#5A7684", width=200, height=300)
        self.app.left_frame.place(relx=0, rely=0, anchor=tkinter.NW)

        image = Image.open(self.app.ICONS_PATH / "logo.png")
        logo_image = customtkinter.CTkImage(light_image=image, dark_image=image, size=(150, 150))

        self.app.logo_label = customtkinter.CTkLabel(self.app.left_frame, text="", image=logo_image)
        self.app.logo_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.app.title_label = customtkinter.CTkLabel(self.app.login_window, text="Login", font=customtkinter.CTkFont(size=32, weight="bold"), text_color="#5A7684")
        self.app.title_label.place(relx=0.7, rely=0.15, anchor=tkinter.CENTER)

        self.app.username_Entry = customtkinter.CTkEntry(self.app.login_window, placeholder_text="Usuário", width=250, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.username_Entry.place(relx=0.7, rely=0.45, anchor=tkinter.CENTER)

        self.app.password_Entry = customtkinter.CTkEntry(self.app.login_window, placeholder_text="Senha", show="•", width=250, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.password_Entry.place(relx=0.7, rely=0.65, anchor=tkinter.CENTER)

        self.app.login_button = customtkinter.CTkButton(self.app.login_window, text="Login", width=250, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=lambda: self.app.autentic("users"))
        self.app.login_button.place(relx=0.7, rely=0.85, anchor=tkinter.CENTER)
        
        self.app.username_Entry.bind("<Return>", lambda event: self.app.autentic("users"))
        self.app.password_Entry.bind("<Return>", lambda event: self.app.autentic("users"))
        
        self.app.settings_button = customtkinter.CTkButton(
            self.app.login_window,
            text="⚙️",
            width=20,
            height=20,
            corner_radius=0,
            fg_color="#5A7684",
            hover_color="#4A6674",
            command=self.show_login_settings
        )
        self.app.settings_button.place(relx=0.05, rely=0.9, anchor=tkinter.CENTER)
        
        self.app.login_window.update_idletasks()
        x = (self.app.login_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.app.login_window.winfo_screenheight() // 2) - (500 // 2)
        self.app.login_window.geometry(f"500x300+{x}+{y}")
        
        self.app.login_window.protocol("WM_DELETE_WINDOW", self.app.exit_app)
        
        self.app.withdraw()

    def window_month_packs(self, client_id=None):
        self.app.month_packs_window = customtkinter.CTkToplevel(self.app)
        self.app.month_packs_window.title("Pacotes Mensais - CleanMax")
        self.app.month_packs_window.geometry("1280x720")
        self.app.month_packs_window.resizable(False, False)
        self.app.month_packs_window.transient(self.app)
        self.app.month_packs_window.grab_set()
        self.app.month_packs_window.focus_force()
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        self.app.month_packs_window.iconbitmap(ico_path)
        
        self.app.month_packs_window.update_idletasks()
        main_x = self.app.winfo_x()
        main_y = self.app.winfo_y()
        main_width = self.app.winfo_width()
        main_height = self.app.winfo_height()
        
        window_width = 1280
        window_height = 720
        
        x = main_x + (main_width - window_width) // 2
        y = main_y + (main_height - window_height) // 2
        
        self.app.month_packs_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.app.month_packs_window.configure(fg_color="#E5E9F2")
        
        cliente = self.app.db_functions.get_cliente_by_id(client_id)
        if cliente:
            self.client_data = {
                'id': cliente[0],
                'name': cliente[1],
                'phone': cliente[2],
                'address': cliente[3]
            }
        else:
            self.client_data = {'id': '', 'name': '', 'phone': '', 'address': ''}
        self.packs_data = self.app.db_functions.get_packs_by_cliente_id(client_id)
        self.create_month_packs_content()

    def create_month_packs_content(self):
        main_frame = customtkinter.CTkFrame(self.app.month_packs_window, fg_color="transparent")
        main_frame.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=20)
        
        title_label = customtkinter.CTkLabel(
            main_frame, 
            text="Pacotes Mensais", 
            font=customtkinter.CTkFont(size=28, weight="bold"), 
            text_color="#5A7684"
        )
        title_label.pack(pady=(0, 20))
        
        content_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill=tkinter.BOTH, expand=True)
        
        left_frame = customtkinter.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        left_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 10))
        
        right_frame = customtkinter.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        right_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=(10, 0))
        
        self.create_client_info_section(left_frame)
        self.create_packs_treeview_section(right_frame)

    def create_client_info_section(self, parent_frame):
        client_title = customtkinter.CTkLabel(
            parent_frame,
            text="Informações do Cliente",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color="#5A7684"
        )
        client_title.pack(pady=20)
        
        fields_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        fields_frame.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=20)
        
        id_label = customtkinter.CTkLabel(fields_frame, text="ID:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        id_label.pack(anchor=tkinter.W, pady=(0, 5))
        
        self.client_id_entry = customtkinter.CTkEntry(fields_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", state="readonly")
        self.client_id_entry.pack(fill=tkinter.X, pady=(0, 15))
        
        nome_label = customtkinter.CTkLabel(fields_frame, text="Nome:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        nome_label.pack(anchor=tkinter.W, pady=(0, 5))
        
        self.client_nome_entry = customtkinter.CTkEntry(fields_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", state="readonly")
        self.client_nome_entry.pack(fill=tkinter.X, pady=(0, 15))
        
        telefone_label = customtkinter.CTkLabel(fields_frame, text="Telefone:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        telefone_label.pack(anchor=tkinter.W, pady=(0, 5))
        
        self.client_telefone_entry = customtkinter.CTkEntry(fields_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", state="readonly")
        self.client_telefone_entry.pack(fill=tkinter.X, pady=(0, 15))
        
        endereco_label = customtkinter.CTkLabel(fields_frame, text="Endereço:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        endereco_label.pack(anchor=tkinter.W, pady=(0, 5))
        
        self.client_endereco_entry = customtkinter.CTkEntry(fields_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", state="readonly")
        self.client_endereco_entry.pack(fill=tkinter.X, pady=(0, 30))
        
        buttons_frame = customtkinter.CTkFrame(fields_frame, fg_color="transparent")
        buttons_frame.pack(fill=tkinter.X)
        
        self.edit_button = customtkinter.CTkButton(
            buttons_frame,
            text="Editar",
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#5A7684",
            text_color="#FFFFFF",
            command=self.enable_edit_mode
        )
        self.edit_button.pack(side=tkinter.LEFT, padx=(0, 10))
        
        self.save_button = customtkinter.CTkButton(
            buttons_frame,
            text="Salvar",
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#28a745",
            text_color="#FFFFFF",
            command=self.save_client_info,
            state="disabled"
        )
        self.save_button.pack(side=tkinter.LEFT, padx=(0, 10))
        
        self.cancel_button = customtkinter.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#dc3545",
            text_color="#FFFFFF",
            command=self.cancel_edit_mode,
            state="disabled"
        )
        self.cancel_button.pack(side=tkinter.LEFT)
        
        self.load_client_data()

    def create_packs_treeview_section(self, parent_frame):
        packs_title = customtkinter.CTkLabel(
            parent_frame,
            text="Pacotes do Cliente",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color="#5A7684"
        )
        packs_title.pack(pady=20)
        
        treeview_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        treeview_frame.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=20)
        
        self.packs_treeview = ttk.Treeview(
            treeview_frame,
            columns=("ID", "Data Início", "Pacote", "Quantidade", "Data Vencimento", "Pagamento", "Código"),
            show="headings",
            height=15
        )
        
        self.packs_treeview.heading("ID", text="ID")
        self.packs_treeview.column("ID", width=50, minwidth=50)
        self.packs_treeview.heading("Data Início", text="Data Início")
        self.packs_treeview.column("Data Início", width=100, minwidth=100)
        self.packs_treeview.heading("Pacote", text="Pacote")
        self.packs_treeview.column("Pacote", width=150, minwidth=150)
        self.packs_treeview.heading("Quantidade", text="Quantidade")
        self.packs_treeview.column("Quantidade", width=100, minwidth=100)
        self.packs_treeview.heading("Data Vencimento", text="Data Vencimento")
        self.packs_treeview.column("Data Vencimento", width=120, minwidth=120)
        self.packs_treeview.heading("Pagamento", text="Pagamento")
        self.packs_treeview.column("Pagamento", width=100, minwidth=100)
        self.packs_treeview.heading("Código", text="Código")
        self.packs_treeview.column("Código", width=100, minwidth=100)
        
        self.packs_treeview.tag_configure('oddrow', background='#F0F0F0')
        self.packs_treeview.tag_configure('evenrow', background='#FFFFFF')
        
        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.packs_treeview.yview)
        self.packs_treeview.configure(yscrollcommand=scrollbar.set)
        
        self.packs_treeview.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        
        for idx, row in enumerate(self.packs_data):
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            self.packs_treeview.insert("", tkinter.END, values=row, tags=(tag,))
        self.packs_treeview.bind("<Double-1>", self.on_pack_double_click)

        self.add_pack_button = customtkinter.CTkButton(parent_frame, text="Adicionar Pacote", fg_color="#4FA3C7", text_color="#FFFFFF", command=self.open_add_pack_window)
        self.add_pack_button.pack(pady=(0, 10))

    def on_pack_double_click(self, event):
        selected_item = self.packs_treeview.selection()
        if not selected_item:
            return
        item_values = self.packs_treeview.item(selected_item[0], "values")
        if len(item_values) >= 7:
            codigo = item_values[6]
            id_cliente = self.client_data.get('id', '')
            self.open_weekly_packs_window(codigo, id_cliente)

    def open_weekly_packs_window(self, codigo, id_cliente):
        weekly_win = customtkinter.CTkToplevel(self.app.month_packs_window)
        weekly_win.title(f"Pacotes Semanais - Código {codigo}")
        weekly_win.geometry("600x500")
        weekly_win.resizable(False, False)
        weekly_win.transient(self.app.month_packs_window)
        weekly_win.lift()
        weekly_win.focus_force()
        weekly_win.grab_set()
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        weekly_win.iconbitmap(ico_path)
        weekly_win.configure(fg_color="#E5E9F2")

        weekly_win.update_idletasks()
        parent_x = self.app.month_packs_window.winfo_x()
        parent_y = self.app.month_packs_window.winfo_y()
        parent_w = self.app.month_packs_window.winfo_width()
        parent_h = self.app.month_packs_window.winfo_height()
        win_w = 600
        win_h = 500
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        weekly_win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        treeview = ttk.Treeview(weekly_win, columns=("id", "data_coleta", "quantidade", "codigo"), show="headings")
        treeview.heading("id", text="ID")
        treeview.column("id", width=50)
        treeview.heading("data_coleta", text="Data Coleta")
        treeview.column("data_coleta", width=150)
        treeview.heading("quantidade", text="Quantidade")
        treeview.column("quantidade", width=100)
        treeview.heading("codigo", text="Código")
        treeview.column("codigo", width=100)
        treeview.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=20)

        try:
            self.app.con_database.cur.execute("SELECT id, sdate, qtd, scodigo FROM sempacks WHERE scodigo=?", (codigo,))
            rows = self.app.con_database.cur.fetchall()
            for idx, row in enumerate(rows):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                treeview.insert("", tkinter.END, values=row, tags=(tag,))
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao buscar pacotes semanais: {ex}")

        cadastrar_btn = customtkinter.CTkButton(weekly_win, text="Cadastrar Pacote Semanal", fg_color="#4FA3C7", text_color="#FFFFFF", command=lambda: self.open_add_weekly_pack_window(id_cliente, codigo, treeview))
        cadastrar_btn.pack(pady=10)

    def open_add_weekly_pack_window(self, id_cliente, codigo, treeview):
        add_weekly_win = customtkinter.CTkToplevel()
        add_weekly_win.title("Cadastrar Pacote Semanal")
        add_weekly_win.geometry("450x350")
        add_weekly_win.resizable(False, False)
        add_weekly_win.grab_set()
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        add_weekly_win.iconbitmap(ico_path)
        add_weekly_win.configure(fg_color="#E5E9F2")

        id_label = customtkinter.CTkLabel(add_weekly_win, text="ID do Cliente:")
        id_label.pack(pady=(20, 0))
        id_entry = customtkinter.CTkEntry(add_weekly_win)
        id_entry.pack()
        id_entry.delete(0, "end")
        id_entry.insert(0, str(id_cliente))
        id_entry.configure(state="disabled")

        from datetime import datetime
        data_atual = datetime.now().strftime("%d/%m/%Y")
        data_label = customtkinter.CTkLabel(add_weekly_win, text="Data de Coleta:")
        data_label.pack(pady=(20, 0))
        data_entry = customtkinter.CTkEntry(add_weekly_win)
        data_entry.pack()
        data_entry.delete(0, "end")
        data_entry.insert(0, data_atual)
        data_entry.configure(state="disabled")

        qtd_label = customtkinter.CTkLabel(add_weekly_win, text="Quantidade:")
        qtd_label.pack(pady=(20, 0))
        qtd_entry = customtkinter.CTkEntry(add_weekly_win)
        qtd_entry.pack()

        btn_frame = customtkinter.CTkFrame(add_weekly_win, fg_color="transparent")
        btn_frame.pack(pady=30)
        cadastrar_btn = customtkinter.CTkButton(
            btn_frame, text="Cadastrar", fg_color="#28a745", text_color="#FFFFFF",
            command=lambda: self.cadastrar_pacote_semanal(id_cliente, data_atual, qtd_entry, codigo, treeview, add_weekly_win)
        )
        cadastrar_btn.pack(side=tkinter.LEFT, padx=10)
        cancelar_btn = customtkinter.CTkButton(btn_frame, text="Cancelar", fg_color="#dc3545", text_color="#FFFFFF", command=add_weekly_win.destroy)
        cancelar_btn.pack(side=tkinter.LEFT, padx=10)

    def cadastrar_pacote_semanal(self, id_cliente, data_atual, qtd_entry, codigo, treeview, win):
        qtd = qtd_entry.get()
        if not qtd.isdigit() or int(qtd) <= 0:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return
        try:
            self.app.con_database.cur.execute(
                "INSERT INTO sempacks (id, sdate, qtd, scodigo) VALUES (?, ?, ?, ?)",
                (id_cliente, data_atual, int(qtd), codigo)
            )
            self.app.con_database.dbase.commit()
            messagebox.showinfo("Sucesso", "Pacote semanal cadastrado com sucesso!")
            win.destroy()
            treeview.delete(*treeview.get_children())
            self.app.con_database.cur.execute("SELECT id, sdate, qtd, scodigo FROM sempacks WHERE scodigo=?", (codigo,))
            rows = self.app.con_database.cur.fetchall()
            for idx, row in enumerate(rows):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                treeview.insert("", tkinter.END, values=row, tags=(tag,))
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao cadastrar pacote semanal: {ex}")

    def open_add_pack_window(self):
        cliente_id = self.client_data.get('id', '')
        data_contratacao = datetime.date.today()
        data_vencimento = data_contratacao + datetime.timedelta(days=30)

        self.add_pack_win = customtkinter.CTkToplevel(self.app.month_packs_window)
        self.add_pack_win.title("Cadastrar Novo Pacote")
        self.add_pack_win.geometry("500x500")
        self.add_pack_win.resizable(False, False)
        self.add_pack_win.grab_set()
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        self.add_pack_win.iconbitmap(ico_path)

        id_label = customtkinter.CTkLabel(self.add_pack_win, text="ID do Cliente:")
        id_label.pack(pady=(20, 0))
        id_entry = customtkinter.CTkEntry(self.add_pack_win, state="readonly")
        id_entry.pack()
        id_entry.insert(0, str(cliente_id))

        data_contratacao_label = customtkinter.CTkLabel(self.add_pack_win, text="Data de Contratação:")
        data_contratacao_label.pack(pady=(20, 0))
        data_contratacao_entry = customtkinter.CTkEntry(self.add_pack_win)
        data_contratacao_entry.pack()
        data_contratacao_entry.insert(0, data_contratacao.strftime("%d/%m/%Y"))

        tipo_label = customtkinter.CTkLabel(self.add_pack_win, text="Tipo de Pacote:")
        tipo_label.pack(pady=(20, 0))
        tipo_combobox = customtkinter.CTkComboBox(self.add_pack_win, values=["lavar", "passar", "lavar e passar"])
        tipo_combobox.pack()
        tipo_combobox.set("lavar")

        qtd_label = customtkinter.CTkLabel(self.add_pack_win, text="Quantidade de Peças:")
        qtd_label.pack(pady=(20, 0))
        qtd_entry = customtkinter.CTkEntry(self.add_pack_win)
        qtd_entry.pack()

        data_vencimento_label = customtkinter.CTkLabel(self.add_pack_win, text="Data de Vencimento:")
        data_vencimento_label.pack(pady=(20, 0))
        data_vencimento_entry = customtkinter.CTkEntry(self.add_pack_win)
        data_vencimento_entry.pack()
        data_vencimento_entry.insert(0, data_vencimento.strftime("%d/%m/%Y"))

        btn_frame = customtkinter.CTkFrame(self.add_pack_win, fg_color="transparent")
        btn_frame.pack(pady=30)
        cadastrar_btn = customtkinter.CTkButton(
            btn_frame, text="Cadastrar", fg_color="#28a745", text_color="#FFFFFF",
            command=lambda: self.cadastrar_pacote_db(
                cliente_id,
                data_contratacao_entry,
                tipo_combobox,
                qtd_entry,
                data_vencimento_entry
            )
        )
        cadastrar_btn.pack(side=tkinter.LEFT, padx=10)
        cancelar_btn = customtkinter.CTkButton(btn_frame, text="Cancelar", fg_color="#dc3545", text_color="#FFFFFF", command=self.add_pack_win.destroy)
        cancelar_btn.pack(side=tkinter.LEFT, padx=10)

    def enable_edit_mode(self):
        self.client_nome_entry.configure(state="normal", fg_color="#FFFFFF")
        self.client_telefone_entry.configure(state="normal", fg_color="#FFFFFF")
        self.client_endereco_entry.configure(state="normal", fg_color="#FFFFFF")
        
        self.edit_button.configure(state="disabled")
        self.save_button.configure(state="normal")
        self.cancel_button.configure(state="normal")

    def save_client_info(self):
        self.disable_edit_mode()
        messagebox.showinfo("Sucesso", "Informações do cliente salvas com sucesso!")

    def cancel_edit_mode(self):
        self.disable_edit_mode()
        messagebox.showinfo("Cancelado", "Edição cancelada!")

    def disable_edit_mode(self):
        self.client_nome_entry.configure(state="readonly", fg_color="#F0F0F0")
        self.client_telefone_entry.configure(state="readonly", fg_color="#F0F0F0")
        self.client_endereco_entry.configure(state="readonly", fg_color="#F0F0F0")
        
        self.edit_button.configure(state="normal")
        self.save_button.configure(state="disabled")
        self.cancel_button.configure(state="disabled")

    def load_sample_packs_data(self):
        for item in self.packs_treeview.get_children():
            self.packs_treeview.delete(item)
        
        client_id = self.client_data['id']
        
        sample_data = [
            (f"{client_id}_1", "01/01/2024", "Pacote Básico", "1", "31/01/2024", "Pago", f"PB{client_id}01"),
            (f"{client_id}_2", "01/02/2024", "Pacote Premium", "2", "29/02/2024", "Pendente", f"PP{client_id}02"),
            (f"{client_id}_3", "01/03/2024", "Pacote Básico", "1", "31/03/2024", "Pago", f"PB{client_id}03"),
        ]
        
        for i, data in enumerate(sample_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.packs_treeview.insert("", "end", values=data, tags=(tag,))

    def load_client_data(self):
        if hasattr(self, 'client_data') and self.client_data:
            self.client_id_entry.configure(state="normal")
            self.client_id_entry.delete(0, tkinter.END)
            self.client_id_entry.insert(0, str(self.client_data.get('id', '')))
            self.client_id_entry.configure(state="readonly")
            
            self.client_nome_entry.configure(state="normal")
            self.client_nome_entry.delete(0, tkinter.END)
            self.client_nome_entry.insert(0, str(self.client_data.get('name', '')))
            self.client_nome_entry.configure(state="readonly")
            
            self.client_telefone_entry.configure(state="normal")
            self.client_telefone_entry.delete(0, tkinter.END)
            self.client_telefone_entry.insert(0, str(self.client_data.get('phone', '')))
            self.client_telefone_entry.configure(state="readonly")
            
            self.client_endereco_entry.configure(state="normal")
            self.client_endereco_entry.delete(0, tkinter.END)
            self.client_endereco_entry.insert(0, str(self.client_data.get('address', '')))
            self.client_endereco_entry.configure(state="readonly")

    def cadastrar_pacote_db(self, cliente_id, data_contratacao_entry, tipo_combobox, qtd_entry, data_vencimento_entry):
        data_contratacao_str = data_contratacao_entry.get()
        data_contratacao_dt = datetime.datetime.strptime(data_contratacao_str, "%d/%m/%Y")
        data_vencimento_dt = data_contratacao_dt + datetime.timedelta(days=30)
        data_vencimento_str = data_vencimento_dt.strftime("%d/%m/%Y")
        tipo = tipo_combobox.get()
        qtd = qtd_entry.get()
        if not qtd.isdigit() or int(qtd) <= 0:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return
        success, msg = self.app.db_functions.cadastrar_pacote(cliente_id, data_contratacao_str, tipo, qtd, data_vencimento_str)
        if success:
            messagebox.showinfo("Sucesso", msg)
            self.add_pack_win.destroy()
            self.packs_data = self.app.db_functions.get_packs_by_cliente_id(cliente_id)
            self.packs_treeview.delete(*self.packs_treeview.get_children())
            for idx, row in enumerate(self.packs_data):
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                self.packs_treeview.insert("", tkinter.END, values=row, tags=(tag,))
        else:
            messagebox.showerror("Erro", msg)

    def show_login_settings(self):
        settings_window = customtkinter.CTkToplevel(self.app.login_window)
        settings_window.title("Configurações")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        settings_window.transient(self.app.login_window)
        settings_window.grab_set()
        settings_window.focus_force()
        settings_window.configure(fg_color="#E5E9F2")
        ico_path = os.path.abspath(self.app.ICONS_PATH / "washer.ico")
        settings_window.iconbitmap(ico_path)
        
        settings_window.update_idletasks()
        login_x = self.app.login_window.winfo_x()
        login_y = self.app.login_window.winfo_y()
        login_w = self.app.login_window.winfo_width()
        login_h = self.app.login_window.winfo_height()
        win_w = 400
        win_h = 300
        x = login_x + (login_w - win_w) // 2
        y = login_y + (login_h - win_h) // 2
        settings_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        title_label = customtkinter.CTkLabel(
            settings_window,
            text="Configurações",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color="#5A7684"
        )
        title_label.pack(pady=30)
        
        def carregar_banco_login():
            arquivo_selecionado = filedialog.askopenfilename(
                title="Selecionar Banco de Dados",
                filetypes=[("Arquivos SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            
            if arquivo_selecionado:
                try:
                    banco_atual = Path(__file__).parent / "cmax.db"
                    
                    if banco_atual.exists():
                        backup_path = Path(__file__).parent / f"cmax_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                        shutil.copy2(banco_atual, backup_path)
                    
                    self.app.con_database.close_connection()
                    
                    shutil.copy2(arquivo_selecionado, banco_atual)
                    
                    self.app.con_database = DataBase()
                    
                    messagebox.showinfo("Sucesso", "Banco de dados carregado com sucesso!")
                    settings_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar banco de dados: {e}")
        
        load_db_button = customtkinter.CTkButton(
            settings_window,
            text="Carregar Banco de Dados",
            width=250,
            height=40,
            corner_radius=8,
            fg_color="#5A7684",
            text_color="#FFFFFF",
            command=carregar_banco_login
        )
        load_db_button.pack(pady=20)
        
        close_button = customtkinter.CTkButton(
            settings_window,
            text="Fechar",
            width=250,
            height=40,
            corner_radius=8,
            fg_color="#dc3545",
            text_color="#FFFFFF",
            command=settings_window.destroy
        )
        close_button.pack(pady=20)