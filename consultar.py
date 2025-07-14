import os
from config import CAMINHO_PDFS
from banco import buscar_cliente

def extrair_nome_primeiro_pdf():
    """Pega o nome base (sem .pdf) do primeiro PDF encontrado na pasta."""
    arquivos = sorted(os.listdir(CAMINHO_PDFS))
    for arquivo in arquivos:
        if arquivo.lower().endswith(".pdf"):
            nome_base = os.path.splitext(arquivo)[0]
            return nome_base
    return None
print("🔎 Primeiro PDF encontrado: ", extrair_nome_primeiro_pdf()) 