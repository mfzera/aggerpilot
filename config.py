# Arquivo: config.py (VERSÃO AJUSTADA)

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Configurações que não foram alteradas ---
# Configurações de conexão SSH lidas do .env
SSH_CONFIG = {
    "hostname": os.getenv("SSH_HOST"),
    "username": os.getenv("SSH_USER"),
    "password": os.getenv("SSH_PASS"),
    "port": 22
}

# Caminho remoto para a pasta de PDFs (mantido para outros possíveis usos)
CAMINHO_REMOTO_PDFS = os.getenv("REMOTO_PDFS")

# String de conexão com o banco de dados (INTOCADO, CONFORME SOLICITADO)
CAMINHO_DB = (
    f"host={os.getenv('DB_HOST')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASS')} "
    f"port={os.getenv('DB_PORT')}"
)

# --- NOVA CONFIGURAÇÃO ADICIONADA ---
# Caminho para a pasta LOCAL no seu computador onde as propostas.pdf estão.
# Esta variável será usada pelo novo main.py.
CAMINHO_LOCAL_PROPOSTAS = os.getenv("LOCAL_PROPOSTAS")