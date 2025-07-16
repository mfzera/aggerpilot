# Arquivo: banco.py (VERSÃO COM BOAS PRÁTICAS)

import psycopg2
from config import CAMINHO_DB

def buscar_cliente(nome_cliente):
    """
    Busca os dados de um cliente no banco de dados usando o nome fornecido.
    A gestão da conexão foi melhorada com o uso de 'with'.
    """
    if not nome_cliente:
        print("❌ Nome do cliente não fornecido para busca no banco.")
        return None

    sql_query = """
        SELECT cliente, produto, observacao, vigencia, situacao, status, vendedor, pct_atual
        FROM registros_vendedor
        WHERE cliente = %s
    """
    
    try:
        print(f"🔎 Buscando dados para o cliente '{nome_cliente}' no banco de dados...")
        # O 'with' garante que a conexão e o cursor sejam fechados automaticamente
        with psycopg2.connect(CAMINHO_DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query, (nome_cliente,))
                resultado = cursor.fetchone()

        # O código a partir daqui permanece o mesmo
        if resultado:
            print("✅ Dados do cliente encontrados!")
            return {
                "nome": resultado[0],
                "item": resultado[1],
                "observacao": resultado[2],
                "vigencia": resultado[3],
                "telefone": "0",  # sempre deve ser 0
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