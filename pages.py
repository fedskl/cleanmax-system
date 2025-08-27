import bcrypt
import customtkinter
import tkinter
import sqlite3
from tkinter import ttk
from windows import Windows
from tkinter import messagebox
from tkinter import filedialog
import shutil
from pathlib import Path
import datetime
from data import DataBase

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

class Pages:
    def __init__(self, app):
        self.app = app
        self.windows = Windows(app)
    
    def validar_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validar_telefone(self, telefone):
        import re
        telefone_limpo = re.sub(r'\D', '', telefone)
        return len(telefone_limpo) in [10, 11]

    def prevenir_xss(self, texto):
        if not texto:
            return texto
        escapes = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }
        for char, escape in escapes.items():
            texto = texto.replace(char, escape)
        return texto
    
    def show_home_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.home_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )

        self.app.home_label = customtkinter.CTkLabel(self.app.main_area, text="Página Inicial", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="#5A7684")
        self.app.home_label.pack(pady=20)

        last_packs_frame = customtkinter.CTkFrame(self.app.main_area, fg_color="white", corner_radius=10)
        last_packs_frame.pack(pady=10, padx=30, fill="x")
        last_packs_label = customtkinter.CTkLabel(last_packs_frame, text="Últimos Pacotes Adicionados", font=customtkinter.CTkFont(size=18, weight="bold"), text_color="#5A7684")
        last_packs_label.pack(pady=(10, 5))
        
        last_packs_tv = ttk.Treeview(last_packs_frame, columns=("ID", "Data Início", "Pacote", "Quantidade", "Vencimento", "Pagamento", "Código"), show="headings", height=5)
        for col in ("ID", "Data Início", "Pacote", "Quantidade", "Vencimento", "Pagamento", "Código"):
            last_packs_tv.heading(col, text=col)
            last_packs_tv.column(col, width=100)
        last_packs_tv.pack(padx=10, pady=10, fill="x")
        
        for row in self.app.db_functions.get_last_packs():
            last_packs_tv.insert("", "end", values=row)

                # Seção de pacotes vencendo
        frame_vencendo = customtkinter.CTkFrame(self.app.main_area, fg_color="white", corner_radius=10)
        frame_vencendo.pack(pady=10, padx=30, fill="x")

        titulo_vencendo = customtkinter.CTkLabel(frame_vencendo, text="Pacotes Próximos do Vencimento", 
                                            font=customtkinter.CTkFont(size=18, weight="bold"), 
                                            text_color="#5A7684")
        titulo_vencendo.pack(pady=(10, 5))

        # Treeview para os pacotes
        tv_vencendo = ttk.Treeview(frame_vencendo, columns=("ID", "Vencimento", "Dias"), 
                                show="headings", height=5)
        tv_vencendo.heading("ID", text="ID Cliente")
        tv_vencendo.heading("Vencimento", text="Data Vencimento")
        tv_vencendo.heading("Dias", text="Dias Restantes")
        tv_vencendo.column("ID", width=80)
        tv_vencendo.column("Vencimento", width=120)
        tv_vencendo.column("Dias", width=100)
        tv_vencendo.pack(padx=10, pady=10, fill="x")

        # Carregar dados
        hoje = datetime.datetime.now()
        packs = self.app.db_functions.get_packs_expiring_soon()

        if packs:
            for pack in packs:
                try:
                    data_venc = datetime.datetime.strptime(pack[1], "%d/%m/%Y")
                    dias_restantes = (data_venc - hoje).days
                    tv_vencendo.insert("", "end", values=(pack[0], pack[1], f"{dias_restantes} dias"))
                except:
                    continue
        else:
            # Mensagem se não houver pacotes vencendo
            label_vazio = customtkinter.CTkLabel(frame_vencendo, text="Nenhum pacote vence nos próximos dias",
                                            text_color="#6c757d", font=customtkinter.CTkFont(size=12))
            label_vazio.pack(pady=10)
    def show_clientes_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.clientes_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )
        self.app.clientes_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.app.clientes_label = customtkinter.CTkLabel(self.app.main_area, text="Clientes", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="#5A7684")
        self.app.clientes_label.pack(pady=20)

        search_frame = customtkinter.CTkFrame(self.app.main_area, fg_color="transparent")
        search_frame.pack(pady=20)

        self.app.search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Buscar cliente", width=200, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.search_entry.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.search_button = customtkinter.CTkButton(search_frame, text="Buscar", width=100, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=self.search_clientes)
        self.app.search_button.pack(side=tkinter.LEFT)
        
        self.app.clear_search_button = customtkinter.CTkButton(search_frame, text="Limpar", width=100, height=40, corner_radius=8, fg_color="#6c757d", text_color="#FFFFFF", command=self.clear_search)
        self.app.clear_search_button.pack(side=tkinter.LEFT, padx=(10, 0))
        
        self.app.search_entry.bind("<Return>", lambda event: self.search_clientes())

        self.app.treeview_clientes = ttk.Treeview(self.app.main_area, columns=("ID", "Nome", "Telefone", "Endereço"), show="headings")
        self.app.treeview_clientes.heading("ID", text="ID")
        self.app.treeview_clientes.column("ID", minwidth=20, width=20)
        self.app.treeview_clientes.heading("Nome", text="Nome")
        self.app.treeview_clientes.column("Nome", minwidth=200, width=200)
        self.app.treeview_clientes.heading("Telefone", text="Telefone")
        self.app.treeview_clientes.column("Telefone", minwidth=100, width=100)
        self.app.treeview_clientes.heading("Endereço", text="Endereço")
        self.app.treeview_clientes.column("Endereço", minwidth=100, width=100)

        self.app.treeview_clientes.tag_configure('oddrow', background='#708090')
        self.app.treeview_clientes.tag_configure('evenrow', background='#FFFFFF')

        self.app.scroll_clientes = customtkinter.CTkScrollbar(self.app.main_area, orientation="vertical", command=self.app.treeview_clientes.yview)
        self.app.scroll_clientes.place(relx=0.95, rely=0.25, relheight=0.73)
        self.app.treeview_clientes.configure(yscrollcommand=self.app.scroll_clientes.set)

        self.app.treeview_clientes.place(relx=0.01, rely=0.25, relwidth=0.94, relheight=0.73)

        self.app.db_functions.show_treeview("customers", self.app.treeview_clientes, filter=0)

        self.app.treeview_clientes.bind("<Double-1>", self.on_client_double_click)

    def on_client_double_click(self, event):
        selected_item = self.app.treeview_clientes.selection()
        if not selected_item:
            return
        item_values = self.app.treeview_clientes.item(selected_item[0], "values")
        if len(item_values) >= 1:
            client_id = item_values[0]
            self.windows.window_month_packs(client_id)

    def show_new_cliente_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.new_cliente_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )
        self.app.new_cliente_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.app.new_cliente_label = customtkinter.CTkLabel(self.app.main_area, text="Cadastrar Cliente", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="#5A7684")
        self.app.new_cliente_label.pack(pady=20)

        self.app.id_cliente_label = customtkinter.CTkLabel(self.app.main_area, text="ID do Cliente", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.id_cliente_label.pack(pady=(20, 5))
        
        self.app.id_cliente_entry = customtkinter.CTkEntry(self.app.main_area, placeholder_text="ID do Cliente", width=300, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.id_cliente_entry.pack(pady=(0, 20))

        self.app.nome_cliente_label = customtkinter.CTkLabel(self.app.main_area, text="Nome do Cliente", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.nome_cliente_label.pack(pady=(0, 5))
        
        self.app.nome_cliente_entry = customtkinter.CTkEntry(self.app.main_area, placeholder_text="Nome do Cliente", width=300, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.nome_cliente_entry.pack(pady=(0, 20))

        self.app.telefone_cliente_label = customtkinter.CTkLabel(self.app.main_area, text="Telefone do Cliente", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.telefone_cliente_label.pack(pady=(0, 5))
        
        self.app.telefone_cliente_entry = customtkinter.CTkEntry(self.app.main_area, placeholder_text="Telefone do Cliente", width=300, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.telefone_cliente_entry.pack(pady=(0, 20))

        self.app.endereco_cliente_label = customtkinter.CTkLabel(self.app.main_area, text="Endereço do Cliente", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.endereco_cliente_label.pack(pady=(0, 5))
        
        self.app.endereco_cliente_entry = customtkinter.CTkEntry(self.app.main_area, placeholder_text="Endereço do Cliente", width=300, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.endereco_cliente_entry.pack(pady=(0, 20))
        
        buttons_frame = customtkinter.CTkFrame(self.app.main_area, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        self.app.new_cliente_button = customtkinter.CTkButton(buttons_frame, text="Cadastrar", width=150, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=self.app.db_functions.insert_cliente)
        self.app.new_cliente_button.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.cancel_button = customtkinter.CTkButton(buttons_frame, text="Cancelar", width=150, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=self.show_clientes_page)
        self.app.cancel_button.pack(side=tkinter.LEFT)

    def show_reports_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.reports_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )

        self.app.reports_btn.pack(fill=tkinter.X, pady=5, padx=0)
        
        main_container = customtkinter.CTkFrame(self.app.main_area, fg_color="transparent")
        main_container.pack(fill=tkinter.BOTH, expand=True, padx=50, pady=30)
        
        self.app.reports_label = customtkinter.CTkLabel(main_container, text="Relatórios", font=customtkinter.CTkFont(size=28, weight="bold"), text_color="#5A7684")
        self.app.reports_label.pack(pady=(0, 40))

        cliente_section = customtkinter.CTkFrame(main_container, fg_color="transparent")
        cliente_section.pack(fill=tkinter.X, pady=(0, 30))
        
        self.app.select_cliente_label = customtkinter.CTkLabel(cliente_section, text="Selecione o Cliente", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.select_cliente_label.pack(pady=(0, 10))

        self.app.select_cliente_entry = customtkinter.CTkEntry(cliente_section, placeholder_text="Informe o ID do Cliente", width=300, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.select_cliente_entry.pack(pady=(0, 10))

        periodo_section = customtkinter.CTkFrame(main_container, fg_color="transparent")
        periodo_section.pack(fill=tkinter.X, pady=(0, 30))
        
        self.app.repotrt_initial_date_label = customtkinter.CTkLabel(periodo_section, text="Data Inicial", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.repotrt_initial_date_label.pack(pady=(0, 10))
        
        initial_date_frame = customtkinter.CTkFrame(periodo_section, fg_color="transparent")
        initial_date_frame.pack(pady=(0, 20))
        
        self.app.day_combo = customtkinter.CTkComboBox(initial_date_frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                                                                       "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", 
                                                                       "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"],
                                             width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.day_combo.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.month_combo = customtkinter.CTkComboBox(initial_date_frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                                             width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.month_combo.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.year_combo = customtkinter.CTkComboBox(initial_date_frame, values=["2024", "2025", "2026", "2027", "2028", "2029", "2030"], 
                                             width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.year_combo.pack(side=tkinter.LEFT)

        self.app.report_final_date_label = customtkinter.CTkLabel(periodo_section, text="Data Final", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#5A7684")
        self.app.report_final_date_label.pack(pady=(0, 10))
        
        final_date_frame = customtkinter.CTkFrame(periodo_section, fg_color="transparent")
        final_date_frame.pack()
        
        self.app.final_day_combo = customtkinter.CTkComboBox(final_date_frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                                                                        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", 
                                                                        "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"],
                                              width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.final_day_combo.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.final_month_combo = customtkinter.CTkComboBox(final_date_frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                                              width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")   
        self.app.final_month_combo.pack(side=tkinter.LEFT, padx=(0, 10))

        self.app.final_year_combo = customtkinter.CTkComboBox(final_date_frame, values=["2024", "2025", "2026", "2027", "2028", "2029", "2030"], 
                                              width=100, height=40, corner_radius=8, fg_color="#FFFFFF", text_color="#5A7684")
        self.app.final_year_combo.pack(side=tkinter.LEFT)

        buttons_section = customtkinter.CTkFrame(main_container, fg_color="transparent")
        buttons_section.pack(fill=tkinter.X, pady=(20, 0))
        
        reports_buttons_frame = customtkinter.CTkFrame(buttons_section, fg_color="transparent")
        reports_buttons_frame.pack()
        
        self.app.reports_button = customtkinter.CTkButton(reports_buttons_frame, text="Gerar Relatório", width=150, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF")
        self.app.reports_button.pack(side=tkinter.LEFT, padx=(0, 10))
        
        def gerar_relatorio_pdf():
            id_cliente = self.app.select_cliente_entry.get()
            if not id_cliente.isdigit():
                messagebox.showerror("Erro", "Digite um ID de cliente válido.")
                return
            self.app.db_functions.GeneratePDF(
                id_cliente=id_cliente,
                data_ini=f"{self.app.day_combo.get()}/{self.app.month_combo.get()}/{self.app.year_combo.get()}",
                data_fim=f"{self.app.final_day_combo.get()}/{self.app.final_month_combo.get()}/{self.app.final_year_combo.get()}"
            )
        self.app.reports_button.configure(command=gerar_relatorio_pdf)

        self.app.reports_cancel_button = customtkinter.CTkButton(reports_buttons_frame, text="Cancelar", width=150, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=self.show_reports_page)
        self.app.reports_cancel_button.pack(side=tkinter.LEFT)

    def show_settings_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.settings_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )
        self.app.settings_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.app.settings_label = customtkinter.CTkLabel(self.app.main_area, text="Configurações", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="#5A7684")
        self.app.settings_label.pack(pady=20)

        self.app.load_database_button = customtkinter.CTkButton(self.app.main_area, text="Carregar Banco de Dados", width=200, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF")
        self.app.load_database_button.pack(pady=20)

        self.app.save_database_button = customtkinter.CTkButton(self.app.main_area, text="Salvar Banco de Dados", width=200, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF")
        self.app.save_database_button.pack(pady=20)

        self.app.manage_users_button = customtkinter.CTkButton(self.app.main_area, text="Gerenciar Usuários", width=200, height=40, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF")
        self.app.manage_users_button.pack(pady=20)

        def carregar_banco_dados():
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
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar banco de dados: {e}")
        
        self.app.load_database_button.configure(command=carregar_banco_dados)

        def salvar_banco_dados():
            arquivo_destino = filedialog.asksaveasfilename(
                title="Salvar Banco de Dados Como",
                defaultextension=".db",
                filetypes=[("Arquivos SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            
            if arquivo_destino:
                try:
                    banco_atual = Path(__file__).parent / "cmax.db"
                    
                    if not banco_atual.exists():
                        messagebox.showerror("Erro", "Banco de dados atual não encontrado!")
                        return
                    
                    shutil.copy2(banco_atual, arquivo_destino)
                    
                    messagebox.showinfo("Sucesso", f"Banco de dados salvo com sucesso em:\n{arquivo_destino}")
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar banco de dados: {e}")
        
        self.app.save_database_button.configure(command=salvar_banco_dados)

        def gerenciar_usuarios():
            self.show_manage_users_page()
        
        self.app.manage_users_button.configure(command=gerenciar_usuarios)

    def show_manage_users_page(self):
        self.app.clear_content()
        self.app.reset_button_styles()

        self.app.settings_btn.configure(
            fg_color="#E5E9F2",
            hover_color="#E5E9F2",
            width=200,
            corner_radius=0,
            text_color="#5A7684"
        )
        self.app.settings_btn.pack(fill=tkinter.X, pady=5, padx=0)

        self.app.manage_users_label = customtkinter.CTkLabel(self.app.main_area, text="Gerenciar Usuários", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="#5A7684")
        self.app.manage_users_label.pack(pady=20)

        main_content_frame = customtkinter.CTkFrame(self.app.main_area, fg_color="transparent")
        main_content_frame.pack(pady=20, padx=50, fill=tkinter.BOTH, expand=True)

        treeview_frame = customtkinter.CTkFrame(main_content_frame, fg_color="transparent")
        treeview_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 10))

        self.app.treeview_users = ttk.Treeview(treeview_frame, columns=("ID", "Usuário"), show="headings", height=10)
        self.app.treeview_users.heading("ID", text="ID")
        self.app.treeview_users.column("ID", width=100, minwidth=100)
        self.app.treeview_users.heading("Usuário", text="Usuário")
        self.app.treeview_users.column("Usuário", width=200, minwidth=200)

        self.app.treeview_users.tag_configure('oddrow', background='#F0F0F0')
        self.app.treeview_users.tag_configure('evenrow', background='#FFFFFF')

        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.app.treeview_users.yview)
        self.app.treeview_users.configure(yscrollcommand=scrollbar.set)

        self.app.treeview_users.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        buttons_frame = customtkinter.CTkFrame(self.app.main_area, fg_color="transparent")
        buttons_frame.pack(pady=20)

        self.app.novo_usuario_button = customtkinter.CTkButton(buttons_frame, text="Novo Usuário", width=120, height=35, corner_radius=8, fg_color="#28a745", text_color="#FFFFFF", command=self.show_new_user_form)
        self.app.novo_usuario_button.pack(side=tkinter.LEFT, padx=10)

        self.app.editar_usuario_button = customtkinter.CTkButton(buttons_frame, text="Editar", width=120, height=35, corner_radius=8, fg_color="#5A7684", text_color="#FFFFFF", command=self.show_edit_user_form)
        self.app.editar_usuario_button.pack(side=tkinter.LEFT, padx=10)

        self.app.excluir_usuario_button = customtkinter.CTkButton(buttons_frame, text="Excluir", width=120, height=35, corner_radius=8, fg_color="#dc3545", text_color="#FFFFFF", command=self.delete_user)
        self.app.excluir_usuario_button.pack(side=tkinter.LEFT, padx=10)

        self.load_users_data()
        self.app.main_content_frame = main_content_frame
    
    def load_users_data(self):
        try:
            self.app.treeview_users.delete(*self.app.treeview_users.get_children())
            
            self.app.con_database.cur.execute("SELECT id, name FROM users ORDER BY id")
            users = self.app.con_database.cur.fetchall()
            
            for idx, user in enumerate(users):
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                self.app.treeview_users.insert("", tkinter.END, values=user, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
    
    def show_new_user_form(self):
        if hasattr(self.app, 'form_frame'):
            self.app.form_frame.destroy()
        
        self.app.form_frame = customtkinter.CTkFrame(self.app.main_content_frame, fg_color="white", corner_radius=10)
        self.app.form_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=(10, 0))
        
        form_title = customtkinter.CTkLabel(self.app.form_frame, text="Novo Usuário", font=customtkinter.CTkFont(size=18, weight="bold"), text_color="#5A7684")
        form_title.pack(pady=20)
        
        id_label = customtkinter.CTkLabel(self.app.form_frame, text="ID:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        id_label.pack(pady=(0, 5))
        self.app.new_user_id_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684")
        self.app.new_user_id_entry.pack(pady=(0, 15))
        
        name_label = customtkinter.CTkLabel(self.app.form_frame, text="Nome:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        name_label.pack(pady=(0, 5))
        self.app.new_user_name_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684")
        self.app.new_user_name_entry.pack(pady=(0, 15))
        
        password_label = customtkinter.CTkLabel(self.app.form_frame, text="Senha:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        password_label.pack(pady=(0, 5))
        self.app.new_user_password_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", show="•")
        self.app.new_user_password_entry.pack(pady=(0, 15))
        
        confirm_password_label = customtkinter.CTkLabel(self.app.form_frame, text="Confirmar Senha:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        confirm_password_label.pack(pady=(0, 5))
        self.app.new_user_confirm_password_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", show="•")
        self.app.new_user_confirm_password_entry.pack(pady=(0, 20))
        
        form_buttons_frame = customtkinter.CTkFrame(self.app.form_frame, fg_color="transparent")
        form_buttons_frame.pack(pady=20)
        
        cadastrar_btn = customtkinter.CTkButton(form_buttons_frame, text="Cadastrar", width=120, height=35, corner_radius=8, fg_color="#28a745", text_color="#FFFFFF", command=self.cadastrar_usuario)
        cadastrar_btn.pack(side=tkinter.LEFT, padx=10)
        
        cancelar_btn = customtkinter.CTkButton(form_buttons_frame, text="Cancelar", width=120, height=35, corner_radius=8, fg_color="#dc3545", text_color="#FFFFFF", command=self.cancelar_formulario)
        cancelar_btn.pack(side=tkinter.LEFT, padx=10)
    
    def show_edit_user_form(self):
        selected = self.app.treeview_users.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione um usuário para editar.")
            return
        
        user_data = self.app.treeview_users.item(selected[0], "values")
        user_id = user_data[0]
        
        try:
            self.app.con_database.cur.execute("SELECT id, name, password FROM users WHERE id=?", (user_id,))
            user = self.app.con_database.cur.fetchone()
            if not user:
                messagebox.showerror("Erro", "Usuário não encontrado.")
                return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar usuário: {e}")
            return
        
        if hasattr(self.app, 'form_frame'):
            self.app.form_frame.destroy()
        
        self.app.form_frame = customtkinter.CTkFrame(self.app.main_content_frame, fg_color="white", corner_radius=10)
        self.app.form_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=(10, 0))
        
        form_title = customtkinter.CTkLabel(self.app.form_frame, text="Editar Usuário", font=customtkinter.CTkFont(size=18, weight="bold"), text_color="#5A7684")
        form_title.pack(pady=20)
        
        id_label = customtkinter.CTkLabel(self.app.form_frame, text="ID:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        id_label.pack(pady=(0, 5))
        self.app.edit_user_id_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", state="readonly")
        self.app.edit_user_id_entry.pack(pady=(0, 15))
        self.app.edit_user_id_entry.insert(0, user[0])
        
        name_label = customtkinter.CTkLabel(self.app.form_frame, text="Nome:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        name_label.pack(pady=(0, 5))
        self.app.edit_user_name_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684")
        self.app.edit_user_name_entry.pack(pady=(0, 15))
        self.app.edit_user_name_entry.insert(0, user[1])
        
        password_label = customtkinter.CTkLabel(self.app.form_frame, text="Senha:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        password_label.pack(pady=(0, 5))
        self.app.edit_user_password_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", show="•")
        self.app.edit_user_password_entry.pack(pady=(0, 15))
        
        confirm_password_label = customtkinter.CTkLabel(self.app.form_frame, text="Confirmar Senha:", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#5A7684")
        confirm_password_label.pack(pady=(0, 5))
        self.app.edit_user_confirm_password_entry = customtkinter.CTkEntry(self.app.form_frame, width=300, height=35, corner_radius=8, fg_color="#F0F0F0", text_color="#5A7684", show="•")
        self.app.edit_user_confirm_password_entry.pack(pady=(0, 20))
        
        form_buttons_frame = customtkinter.CTkFrame(self.app.form_frame, fg_color="transparent")
        form_buttons_frame.pack(pady=20)
        
        salvar_btn = customtkinter.CTkButton(form_buttons_frame, text="Salvar", width=120, height=35, corner_radius=8, fg_color="#28a745", text_color="#FFFFFF", command=self.salvar_edicao_usuario)
        salvar_btn.pack(side=tkinter.LEFT, padx=10)
        
        cancelar_btn = customtkinter.CTkButton(form_buttons_frame, text="Cancelar", width=120, height=35, corner_radius=8, fg_color="#dc3545", text_color="#FFFFFF", command=self.cancelar_formulario)
        cancelar_btn.pack(side=tkinter.LEFT, padx=10)

    def cadastrar_usuario(self):
        try:
            user_id = self.app.new_user_id_entry.get().strip()
            name = self.app.new_user_name_entry.get().strip()
            password = self.app.new_user_password_entry.get()
            confirm_password = self.app.new_user_confirm_password_entry.get()
            
            if not user_id or not name or not password or not confirm_password:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return
            
            if not user_id.isdigit():
                messagebox.showerror("Erro", "ID deve ser um número!")
                return
            
            if password != confirm_password:
                messagebox.showerror("Erro", "Senhas não coincidem!")
                return
            
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            self.app.con_database.cur.execute(
                "INSERT INTO users (id, name, password) VALUES (?, ?, ?)",
                (user_id, name, hashed_password)
            )
            self.app.con_database.dbase.commit()
            
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            
            self.cancelar_formulario()
            self.load_users_data()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "ID de usuário já existe!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")

    def salvar_edicao_usuario(self):
        try:
            user_id = self.app.edit_user_id_entry.get().strip()
            name = self.app.edit_user_name_entry.get().strip()
            password = self.app.edit_user_password_entry.get()
            confirm_password = self.app.edit_user_confirm_password_entry.get()
            
            if not name:
                messagebox.showerror("Erro", "Nome é obrigatório!")
                return
            
            if password != confirm_password:
                messagebox.showerror("Erro", "Senhas não coincidem!")
                return
            
            if password:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            else:
                self.app.con_database.cur.execute("SELECT password FROM users WHERE id=?", (user_id,))
                hashed_password = self.app.con_database.cur.fetchone()[0]
            
            self.app.con_database.cur.execute(
                "UPDATE users SET name=?, password=? WHERE id=?", 
                (name, hashed_password, user_id)
            )
            self.app.con_database.dbase.commit()
            
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            
            self.cancelar_formulario()
            self.load_users_data()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {e}")
    
    def delete_user(self):
        selected = self.app.treeview_users.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione um usuário para excluir.")
            return
        
        user_data = self.app.treeview_users.item(selected[0], "values")
        confirm = messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário '{user_data[1]}'?")
        
        if confirm:
            try:
                user_id = user_data[0]
                self.app.con_database.cur.execute("DELETE FROM users WHERE id=?", (user_id,))
                self.app.con_database.dbase.commit()
                
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
                
                self.load_users_data()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}")
    
    def cancelar_formulario(self):
        if hasattr(self.app, 'form_frame'):
            self.app.form_frame.destroy()

    def search_clientes(self):
        search_term = self.app.search_entry.get().strip()
        
        if not search_term:
            self.app.db_functions.show_treeview("customers", self.app.treeview_clientes, filter=0)
            return
        
        clientes_encontrados = self.app.db_functions.search_clientes_by_name(search_term)
        
        self.app.treeview_clientes.delete(*self.app.treeview_clientes.get_children())
        
        for idx, cliente in enumerate(clientes_encontrados):
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            self.app.treeview_clientes.insert("", tkinter.END, values=cliente, tags=(tag,))
        
        if not clientes_encontrados:
            messagebox.showinfo("Busca", f"Nenhum cliente encontrado com o nome '{search_term}'")

    def clear_search(self):
        self.app.search_entry.delete(0, tkinter.END)
        self.app.db_functions.show_treeview("customers", self.app.treeview_clientes, filter=0)