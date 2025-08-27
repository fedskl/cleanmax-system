import sqlite3
from sqlite3 import Error
from pathlib import Path
from tkinter import messagebox

class DataBase:
    def __init__(self, db_name="cmax.db"):
        try:
            db_path = Path(__file__).parent / db_name
            self.dbase = sqlite3.connect(db_path)
            self.cur = self.dbase.cursor()
            self.criar_tabelas_automaticamente()
        
        except Error as e:
            self._show_error("Failed to connect to database", e)

    def _show_error(self, title, error):
        messagebox.showerror(title=title, message=f"{title}: {error}")

    def execute_query(self, query, params=None):
        try:
            with self.dbase:
                if params:
                    self.cur.execute(query, params)
                else:
                    self.cur.execute(query)
                return self.cur.fetchall()
        except Error as e:
            self._show_error("Failed to execute query", e)
            return None

    def tables(self, ddl):
        self.execute_query(ddl)

    def manipulation(self, dml, params=None):
        try:
            with self.dbase:
                if params:
                    self.cur.execute(dml, params)
                else:
                    self.cur.execute(dml)
                self.dbase.commit()
                
        except Error as e:
            self._show_error("Failed to execute manipulation", e)

    def show_all(self, tablename):
        query = f"SELECT * FROM {tablename}"
        rows = self.execute_query(query)
        if rows:
            for row in rows:
                print(row)

    def close_connection(self):
        try:
            if self.dbase:
                self.dbase.close()
        except Error as e:
            self._show_error("Failed to close database connection", e)


    def criar_tabelas_automaticamente(self):
        try:
            # Tabela usuários
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            
            # Tabela clientes
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT
                )
            """)
            
            # Tabela pacotes mensais
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS packs (
                    id INTEGER,
                    in_date TEXT,
                    pack TEXT,
                    qtd INTEGER,
                    venc TEXT,
                    pgto TEXT,
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    FOREIGN KEY (id) REFERENCES customers (id)
                )
            """)
            
            # Tabela pacotes semanais
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS sempacks (
                    id INTEGER,
                    sdate TEXT,
                    qtd INTEGER,
                    scodigo INTEGER,
                    FOREIGN KEY (id) REFERENCES customers (id),
                    FOREIGN KEY (scodigo) REFERENCES packs (codigo)
                )
            """)
            
            # Inserir usuário admin padrão
            self.cur.execute("SELECT COUNT(*) FROM users")
            if self.cur.fetchone()[0] == 0:
                import bcrypt
                senha_hash = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
                self.cur.execute(
                    "INSERT INTO users (id, name, password) VALUES (?, ?, ?)",
                    (1, "admin", senha_hash)
                )
                print("Usuário admin criado: admin/admin")
            
            self.dbase.commit()
            print("Tabelas criadas/com verificadas com sucesso!")
            
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
if __name__ == "__main__":
    db = DataBase()