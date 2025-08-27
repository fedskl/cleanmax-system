import bcrypt
import sqlite3
from pathlib import Path

def migrar_senhas():
    db_path = Path(__file__).parent / "cmax.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT id, name, password FROM users")
    usuarios = cur.fetchall()
    
    for usuario_id, usuario_name, senha_texto in usuarios:
        try:
            if senha_texto is None:
                continue
                
            if isinstance(senha_texto, bytes):
                senha_str = senha_texto.decode('utf-8')
            else:
                senha_str = str(senha_texto)
            
            if senha_str.startswith('$2b$'):
                print(f"Senha do usuário {usuario_name} ({usuario_id}) já está em hash")
                continue
            
            salt = bcrypt.gensalt()
            
            if isinstance(senha_texto, bytes):
                senha_para_hash = senha_texto.decode('utf-8')
            else:
                senha_para_hash = str(senha_texto)
            
            senha_hash = bcrypt.hashpw(senha_para_hash.encode('utf-8'), salt)
            
            cur.execute("UPDATE users SET password = ? WHERE id = ?", 
                       (senha_hash, usuario_id))
            print(f"Senha do usuário {usuario_name} ({usuario_id}) migrada para hash")
            
        except Exception as e:
            print(f"Erro ao migrar usuário {usuario_id} ({usuario_name}): {e}")
            print(f"Tipo da senha: {type(senha_texto)}, Valor: {senha_texto}")
    
    conn.commit()
    conn.close()
    print("Migração concluída!")

if __name__ == "__main__":
    migrar_senhas()