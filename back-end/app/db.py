import MySQLdb
from dotenv import load_dotenv
import os

# Carregar variáveis do .env
load_dotenv()

def get_db_connection():
    try:
        connection = MySQLdb.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            passwd=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DB"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            charset='utf8mb4'
        )
        print("Conexão com MySQL estabelecida com sucesso!")
        return connection
    except MySQLdb.Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Testar a conexão ao rodar o arquivo
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
