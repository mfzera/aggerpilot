# Arquivo: banco.py (VERSÃO FINAL ATUALIZADA)

import psycopg2
from config import CAMINHO_DB

def buscar_cliente(nome_cliente):
    """
    Busca os dados mais recentes de um cliente e todos os seus anexos associados.
    A busca de cliente ignora espaços extras e diferenças de maiúsculas/minúsculas.
    A busca de anexos é feita através do ID do registro do cliente.
    """
    if not nome_cliente:
        print("❌ Nome do cliente não fornecido para busca no banco.")
        return None

    sql_query_cliente = """
        SELECT id, cliente, produto, observacao, situacao, status, vendedor, pct_atual, salvo_por, data_atualizacao
        FROM registros_vendedor
        WHERE trim(lower(cliente)) = trim(lower(%s))
        ORDER BY data_atualizacao DESC
        LIMIT 1
    """
    
    try:
        print(f"🔎 Buscando dados mais recentes para o cliente '{nome_cliente}' no banco de dados...")
        with psycopg2.connect(CAMINHO_DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query_cliente, (nome_cliente,))
                resultado_cliente = cursor.fetchone()

                if not resultado_cliente:
                    print(f"❌ Nenhum registro encontrado para o cliente '{nome_cliente}'.")
                    return None

                print("✅ Dados do cliente encontrados! Buscando anexos associados...")

                registro_id = resultado_cliente[0]

                # --- CORREÇÃO APLICADA AQUI ---
                sql_query_anexos = """
                    SELECT file_path 
                    FROM anexos 
                    WHERE registro_id = %s
                """
                cursor.execute(sql_query_anexos, (registro_id,))
                
                resultados_anexos = cursor.fetchall()
                
                lista_de_anexos = [item[0] for item in resultados_anexos] if resultados_anexos else []

                print(f"✅ {len(lista_de_anexos)} anexo(s) encontrado(s).")

                return {
                    "id": resultado_cliente[0], # <--- ADICIONADO o ID do registro aqui.
                    "nome": resultado_cliente[1],
                    "item": resultado_cliente[2],
                    "observacao": resultado_cliente[3],
                    "telefone": "0",
                    "situacao": resultado_cliente[4],
                    "status": resultado_cliente[5],
                    "vendedor": resultado_cliente[6],
                    "pct_atual": resultado_cliente[7],
                    "salvo_por": resultado_cliente[8],
                    "data_atualizacao": resultado_cliente[9].strftime('%Y-%m-%d %H:%M:%S') if resultado_cliente[9] else None,
                    "anexos": lista_de_anexos 
                }
                
    except Exception as e:
        print(f"🚨 Erro ao conectar ou buscar no banco de dados: {e}")
        return None