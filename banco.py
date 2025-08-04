import psycopg2
from config import CAMINHO_DB

def buscar_cliente(nome_cliente):
    """
    Busca os dados mais recentes de um cliente no banco de dados usando o nome fornecido.
    A busca ignora espaços extras e diferenças de maiúsculas/minúsculas.
    """
    if not nome_cliente:
        print("❌ Nome do cliente não fornecido para busca no banco.")
        return None

    sql_query = """
        SELECT cliente, produto, observacao, situacao, status, vendedor, pct_atual, salvo_por, data_atualizacao
        FROM registros_vendedor
        WHERE trim(lower(cliente)) = trim(lower(%s))
        ORDER BY data_atualizacao DESC
        LIMIT 1
    """
    
    try:
        print(f"🔎 Buscando dados mais recentes para o cliente '{nome_cliente}' no banco de dados...")
        with psycopg2.connect(CAMINHO_DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query, (nome_cliente,))
                resultado = cursor.fetchone()

        if resultado:
            print("✅ Dados do cliente encontrados!")
            return {
                "nome": resultado[0],
                "item": resultado[1],
                "observacao": resultado[2],
                "telefone": "0",
                "situacao": resultado[3],
                "status": resultado[4],
                "vendedor": resultado[5],
                "pct_atual": resultado[6],
                "salvo_por": resultado[7],
                "data_atualizacao": resultado[8].strftime('%Y-%m-%d %H:%M:%S') if resultado[8] else None
            }
        else:
            print(f"❌ Nenhum registro encontrado para o cliente '{nome_cliente}'.")
            return None
            
    except Exception as e:
        print(f"🚨 Erro ao conectar ou buscar no banco de dados: {e}")
        return None
