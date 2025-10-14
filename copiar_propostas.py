# Arquivo: copiar_propostas.py (VERSÃO CORRIGIDA PARA RENOMEAR COM ID DURANTE O DOWNLOAD)

import os
import re
from gerenciador_sftp import GerenciadorSFTP
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS, CAMINHO_LOCAL_PROPOSTAS
from banco import buscar_cliente # IMPORTAR A FUNÇÃO DE BUSCA

def copiar_propostas_da_vps():
    """
    Baixa os arquivos da VPS, busca o ID do cliente no banco
    e salva o arquivo localmente com o padrão 'ID NOME_CLIENTE.extensao'.
    """
    print("--- INICIANDO SINCRONIZAÇÃO DE PROPOSTAS DA VPS ---")
    
    pasta_local = CAMINHO_LOCAL_PROPOSTAS
    if not pasta_local:
        print("🚨 ERRO: CAMINHO_LOCAL_PROPOSTAS não está definido em seu config.py/.env.")
        return False

    if not os.path.exists(pasta_local):
        os.makedirs(pasta_local)
        print(f"✅ Pasta local '{pasta_local}' criada com sucesso.")

    try:
        with GerenciadorSFTP(SSH_CONFIG) as sftp:
            print(f"🌐 Conectado ao VPS. Buscando arquivos em: {CAMINHO_REMOTO_PDFS}")
            
            arquivos_remotos = sftp.listar_arquivos(CAMINHO_REMOTO_PDFS)

            if not arquivos_remotos:
                print("ℹ️ Nenhum arquivo novo encontrado no servidor para baixar.")
                return True

            print(f"✅ Encontrados {len(arquivos_remotos)} arquivos no servidor.")
            arquivos_baixados = 0

            for nome_arquivo_remoto in arquivos_remotos:
                # Extrai o nome do cliente do nome do arquivo (sem extensão e sufixos numéricos)
                nome_base_remoto = os.path.splitext(nome_arquivo_remoto)[0]
                nome_cliente_para_busca = re.sub(r'\d+$', '', nome_base_remoto).strip()

                # Busca o cliente no banco de dados para obter o ID
                print(f"--- \n🔎 Buscando ID para o cliente: '{nome_cliente_para_busca}'")
                dados_cliente = buscar_cliente(nome_cliente_para_busca)

                if not dados_cliente or 'id' not in dados_cliente:
                    print(f"⚠️  Não foi possível encontrar o ID para '{nome_cliente_para_busca}'. Pulando o download deste arquivo.")
                    continue
                
                client_id = dados_cliente['id']
                print(f"✅ ID encontrado: {client_id}")

                # Monta o novo nome do arquivo local com o ID
                novo_nome_local = f"{client_id} {nome_arquivo_remoto}"
                
                caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_arquivo_remoto}"
                caminho_local_completo = os.path.join(pasta_local, novo_nome_local)
                
                if os.path.exists(caminho_local_completo):
                    print(f"🔄 Arquivo '{novo_nome_local}' já existe localmente. Pulando.")
                    continue
                
                print(f"⬇️  Baixando '{nome_arquivo_remoto}' como '{novo_nome_local}'...")
                sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)
                arquivos_baixados += 1

        print(f"\n--- SINCRONIZAÇÃO FINALIZADA. {arquivos_baixados} NOVOS ARQUIVOS BAIXADOS ---")
        return True
    
    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado durante a sincronização: {e}")
        return False


if __name__ == "__main__":
    copiar_propostas_da_vps()