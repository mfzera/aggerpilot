# Arquivo: banco.py (VERSÃO COM DATA ESPECÍFICA DE PROSPECÇÃO)

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

# --- NOVA FUNÇÃO: ATUALIZANDO 'data_prospectada' ---
def atualizar_data_prospectada(registro_id: int) -> bool:
    """
    Atualiza a coluna data_prospectada do registro do cliente com o timestamp atual.
    A atualização só deve ocorrer após o sucesso do processo no Agger.
    """
    if not registro_id:
        print("❌ ID do registro não fornecido para atualização.")
        return False

    # Comando SQL alterado para a nova coluna!
    sql_update = """
        UPDATE registros_vendedor
        SET data_prospectada = NOW() 
        WHERE id = %s
    """

    try:
        print(f"🔄 Tentando atualizar data de prospecção para o registro ID {registro_id} no banco de dados...")
        with psycopg2.connect(CAMINHO_DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_update, (registro_id,))
                conn.commit() 
                if cursor.rowcount > 0:
                    print(f"✅ Data de prospecção do registro ID {registro_id} atualizada com sucesso.")
                    return True
                else:
                    print(f"⚠️ Nenhuma linha afetada ao tentar atualizar o registro ID {registro_id}.")
                    return False

    except Exception as e:
        print(f"🚨 Erro ao atualizar a data de prospecção no banco de dados: {e}")
        return False