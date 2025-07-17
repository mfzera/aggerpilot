# Arquivo: banco.py (VERSÃO COM BUSCA ROBUSTA)

import psycopg2
from config import CAMINHO_DB

def buscar_cliente(nome_cliente):
    """
    Busca os dados de um cliente no banco de dados usando o nome fornecido.
    A busca agora ignora espaços extras e diferenças de maiúsculas/minúsculas.
    """
    if not nome_cliente:
        print("❌ Nome do cliente não fornecido para busca no banco.")
        return None

    # --- MUDANÇA AQUI ---
    # A query agora usa lower() e trim() para uma busca flexível.
    sql_query = """
        SELECT cliente, produto, observacao, vigencia, situacao, status, vendedor, pct_atual
        FROM registros_vendedor
        WHERE trim(lower(cliente)) = trim(lower(%s))
    """
    
    try:
        print(f"🔎 Buscando dados para o cliente '{nome_cliente}' no banco de dados...")
        with psycopg2.connect(CAMINHO_DB) as conn:
            with conn.cursor() as cursor:
                # Passa o nome do cliente para a query
                cursor.execute(sql_query, (nome_cliente,))
                resultado = cursor.fetchone()

        if resultado:
            print("✅ Dados do cliente encontrados!")
            return {
                "nome": resultado[0],
                "item": resultado[1],
                "observacao": resultado[2],
                "vigencia": resultado[3],
                "telefone": "0",
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
