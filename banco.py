# Arquivo: banco.py (VERSÃO CORRIGIDA E FINAL)

import psycopg2
from config import CAMINHO_DB

def buscar_cliente(nome_cliente):
    """
    Busca os dados de um cliente no banco de dados usando o nome fornecido.
    """
    if not nome_cliente:
        print("❌ Nome do cliente não fornecido para busca no banco.")
        return None

    try:
        print(f"🔎 Buscando dados para o cliente '{nome_cliente}' no banco de dados...")
        conn = psycopg2.connect(CAMINHO_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cliente, produto, observacao, vigencia, situacao, status, vendedor, pct_atual
            FROM registros_vendedor
            WHERE cliente = %s
        """, (nome_cliente,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            print("✅ Dados do cliente encontrados!")
            return {
                "nome": resultado[0],
                "item": resultado[1],
                "observacao": resultado[2],
                "vigencia": resultado[3],
                "telefone": "0", # sempre deve ser 0
                "situacao": resultado[4],
                "status": resultado[5],
                "vendedor": resultado[6],
                "pct_atual": resultado[7]
            }
        else:
            print(f"❌ Nenhum registro encontrado para o cliente '{nome_cliente}'.")
            return None
    except Exception as e:
        print(f"🚨 Erro ao conectar ou buscar no banco de dados: {e}")
        return None