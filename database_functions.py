import tkinter
from tkinter import messagebox
import sqlite3
import datetime
from reportlab.pdfgen import canvas
import os.path as path
from tkinter import filedialog
import datetime

class DatabaseFunctions:
    def __init__(self, app):
        self.app = app

    def show_treeview(self, tablename, tvw, filter=None):
        try:
            tvw.delete(*tvw.get_children())

            if filter is None:
                return

            elif filter == 0:
                self.app.con_database.cur.execute(f"SELECT * FROM {tablename} ORDER BY id ASC")

            elif isinstance(filter, int):
                self.app.con_database.cur.execute(f"SELECT * FROM {tablename} WHERE id=?", (filter,))

            elif isinstance(filter, dict):
                for key, value in filter.items():
                    self.app.con_database.cur.execute(f"SELECT * FROM {tablename} WHERE {key}=?", (value,))
                    break

            fetch = self.app.con_database.cur.fetchall()
            for idx, row in enumerate(fetch):
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                tvw.insert("", tkinter.END, values=row, tags=(tag,))

        except Exception as ex:
            messagebox.showerror(title="Erro", message=f"Erro ao carregar dados: {ex}")

    def insert_cliente(self):
        try:
            nome = self.app.pages.prevenir_xss(self.app.nome_cliente_entry.get())
            telefone = self.app.pages.prevenir_xss(self.app.telefone_cliente_entry.get())
            endereco = self.app.pages.prevenir_xss(self.app.endereco_cliente_entry.get())
        
            if not self.app.pages.validar_telefone(telefone):
                messagebox.showerror("Erro", "Telefone inválido!")
                return
            
            dml = "INSERT INTO customers (id, name, phone, address) VALUES (?, ?, ?, ?)"
            params = (
                int(self.app.id_cliente_entry.get()),
                self.app.nome_cliente_entry.get(),
                self.app.telefone_cliente_entry.get(),
                self.app.endereco_cliente_entry.get()
            )
            self.app.con_database.manipulation(dml, params)
            messagebox.showinfo(title="Sucesso", message="Cliente inserido com sucesso")

        except sqlite3.Error as e:
            messagebox.showerror(title="Erro", message=f"Erro ao inserir cliente: {e}")
            self.app.id_cliente_entry.delete(0, tkinter.END)
            self.app.nome_cliente_entry.delete(0, tkinter.END)
            self.app.telefone_cliente_entry.delete(0, tkinter.END)
            self.app.endereco_cliente_entry.delete(0, tkinter.END)

            self.show_treeview("customers", self.app.treeview_clientes, filter=0)

    def get_cliente_by_id(self, cliente_id):
        try:
            self.app.con_database.cur.execute("SELECT * FROM customers WHERE id=?", (cliente_id,))
            return self.app.con_database.cur.fetchone()
        except Exception as ex:
            messagebox.showerror(title="Erro", message=f"Erro ao buscar cliente: {ex}")
            return None

    def get_packs_by_cliente_id(self, cliente_id):
        try:
            self.app.con_database.cur.execute("SELECT * FROM packs WHERE id=?", (cliente_id,))
            return self.app.con_database.cur.fetchall()
        except Exception as ex:
            messagebox.showerror(title="Erro", message=f"Erro ao buscar pacotes: {ex}")
            return []

    def cadastrar_pacote(self, cliente_id, data_contratacao_str, tipo, qtd, data_vencimento_str):
        try:
            self.app.con_database.cur.execute(
                "INSERT INTO packs (id, in_date, pack, qtd, venc, pgto) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    cliente_id,
                    data_contratacao_str,
                    tipo,
                    int(qtd),
                    data_vencimento_str,
                    "Pendente"
                )
            )
            self.app.con_database.dbase.commit()
            return True, "Pacote cadastrado com sucesso!"
        except Exception as ex:
            return False, f"Erro ao cadastrar pacote: {ex}"

    def GeneratePDF(self, id_cliente, data_ini, data_fim):
        try:
            cliente = self.get_cliente_by_id(id_cliente)
            if not cliente:
                messagebox.showerror(title="Erro", message="Cliente não encontrado.")
                return
            
            pdf_file = filedialog.asksaveasfilename(
                title="Salvar Relatório PDF",
                defaultextension=".pdf",
                initialfile=f"Relatorio_{cliente[1]}.pdf",
                filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
            )
            
            if not pdf_file:
                return

            self._report = canvas.Canvas(pdf_file)
            self._report.setPageSize((595, 842))

            logo_path = self.app.ICONS_PATH / "Logo_2.png"
            if logo_path.exists():
                self._report.drawImage(str(logo_path), 450, 750, width=100, height=80)

            self._report.setFont("Helvetica-Bold", 24)
            self._report.setFillColorRGB(0.1, 0.4, 0.6)
            self._report.drawString(40, 800, "CleanMax Lavanderia")
            self._report.setFont("Helvetica", 12)
            self._report.setFillColorRGB(0, 0, 0)
            self._report.drawString(40, 780, "Relatório de Cliente")
            self._report.drawString(40, 760, f"Cliente: {cliente[1]}")
            self._report.drawString(40, 740, f"ID: {cliente[0]}")
            self._report.line(40, 730, 555, 730)

            self._report.setFont("Helvetica-Bold", 14)
            self._report.setFillColorRGB(0.1, 0.4, 0.6)
            self._report.drawString(40, 710, "Coletas Semanais")
            self._report.setFont("Helvetica", 12)
            self._report.setFillColorRGB(0, 0, 0)

            self._report.drawString(40, 690, "Data")
            self._report.drawString(140, 690, "Quantidade")
            self._report.drawString(240, 690, "Código")
            self._report.line(40, 685, 555, 685)
            y = 670

            self.app.con_database.cur.execute("SELECT * FROM sempacks WHERE id=?", (id_cliente,))
            weekly_packs = self.app.con_database.cur.fetchall()
            total_weekly = 0

            for week_pack in weekly_packs:
                date_1 = datetime.datetime.strptime(week_pack[1], "%d/%m/%Y")
                data_filter_ini = datetime.datetime.strptime(data_ini, "%d/%m/%Y")
                data_filter_end = datetime.datetime.strptime(data_fim, "%d/%m/%Y")
                if data_filter_ini <= date_1 <= data_filter_end:
                    self._report.drawString(40, y, week_pack[1])
                    self._report.drawString(140, y, str(week_pack[2]))
                    self._report.drawString(240, y, str(week_pack[3]))
                    total_weekly += week_pack[2]
                    y -= 20

            self._report.setFont("Helvetica-Bold", 12)
            self._report.drawString(40, y, f"Total de Coletas Semanais: {total_weekly}")
            y -= 40

            self._report.setFont("Helvetica-Bold", 14)
            self._report.setFillColorRGB(0.1, 0.4, 0.6)
            self._report.drawString(40, y, "Pacotes Mensais")
            y -= 20
            self._report.setFont("Helvetica", 12)
            self._report.setFillColorRGB(0, 0, 0)

            self._report.drawString(40, y, "Data Inicial")
            self._report.drawString(140, y, "Pacote")
            self._report.drawString(240, y, "Quantidade")
            self._report.drawString(340, y, "Vencimento")
            self._report.drawString(440, y, "Pagamento")
            self._report.line(40, y - 5, 555, y - 5)
            y -= 20

            self.app.con_database.cur.execute("SELECT * FROM packs WHERE id=?", (id_cliente,))
            monthly_packs = self.app.con_database.cur.fetchall()

            for pack in monthly_packs:
                data_ini_pack = datetime.datetime.strptime(pack[1], "%d/%m/%Y")
                data_filter_ini = datetime.datetime.strptime(data_ini, "%d/%m/%Y")
                data_filter_end = datetime.datetime.strptime(data_fim, "%d/%m/%Y")
                if data_filter_ini <= data_ini_pack <= data_filter_end:
                    self._report.drawString(40, y, pack[1])
                    self._report.drawString(140, y, pack[2])
                    self._report.drawString(240, y, str(pack[3]))
                    self._report.drawString(340, y, pack[4])
                    self._report.drawString(440, y, pack[5])
                    y -= 20

            self._report.setFont("Helvetica-Oblique", 10)
            self._report.setFillColorRGB(0.5, 0.5, 0.5)
            self._report.drawString(40, 50, "CleanMax Lavanderia - Relatório Gerado Automaticamente")
            self._report.drawString(500, 50, datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

            self._report.save()
            messagebox.showinfo(title="Sucesso", message=f"Relatório gerado com sucesso em:\n{pdf_file}")

        except Exception as er:
            messagebox.showerror(title="Erro", message=f"Erro ao gerar o relatório:\n{er}")

    def get_last_packs(self, limit=5):
        try:
            self.app.con_database.cur.execute("SELECT * FROM packs ORDER BY rowid DESC LIMIT ?", (limit,))
            return self.app.con_database.cur.fetchall()
        except Exception as ex:
            messagebox.showerror(title="Erro", message=f"Erro ao buscar últimos pacotes: {ex}")
            return []
    
    def get_packs_expiring_soon(self, days=5):
        try:
            hoje = datetime.datetime.now()
            print(f"Data atual do sistema: {hoje.strftime('%d/%m/%Y')}")
            
            packs_vencendo = []
            
            self.app.con_database.cur.execute("SELECT id, venc FROM packs")
            todos_packs = self.app.con_database.cur.fetchall()
            
            print(f"Total de pacotes no banco: {len(todos_packs)}")
            
            for pack in todos_packs:
                id_cliente, data_venc_str = pack
                
                try:
                    data_venc = datetime.datetime.strptime(data_venc_str, "%d/%m/%Y")

                    dias_restantes = (data_venc - hoje).days
                    
                    print(f"Pacote {id_cliente}: vence em {data_venc_str} → {dias_restantes} dias restantes")
                    
                    if dias_restantes >= 0 and dias_restantes <= days:
                        print(f"  → Vence dentro de {days} dias!")
                        packs_vencendo.append(pack)
                    else:
                        print(f"  → Fora do período ({dias_restantes} dias)")
                        
                except ValueError as e:
                    print(f"Erro: Data inválida '{data_venc_str}' - {e}")
                    continue
            
            print(f"Pacotes que vencem em até {days} dias: {len(packs_vencendo)}")
            return packs_vencendo
            
        except Exception as erro:
            print(f"Erro ao verificar vencimentos: {erro}")
            return []
            
    def search_clientes_by_name(self, search_term):
        try:
            self.app.con_database.cur.execute(
                "SELECT * FROM customers WHERE name LIKE ? ORDER BY name ASC",
                (f"%{search_term}%",)
            )
            return self.app.con_database.cur.fetchall()
        except Exception as ex:
            messagebox.showerror(title="Erro", message=f"Erro ao buscar clientes: {ex}")
            return []