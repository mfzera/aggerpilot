# Arquivo: config.py (VERSÃO CORRIGIDA E FINAL)

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Configurações de conexão SSH lidas do .env
SSH_CONFIG = {
    "hostname": os.getenv("SSH_HOST"),
    "username": os.getenv("SSH_USER"),
    "password": os.getenv("SSH_PASS"),
    "port": 22
}

# Caminho remoto para a pasta de PDFs
CAMINHO_REMOTO_PDFS = os.getenv("REMOTO_PDFS")

# String de conexão com o banco de dados
CAMINHO_DB = (
    f"host={os.getenv('DB_HOST')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASS')} "
    f"port={os.getenv('DB_PORT')}"
)