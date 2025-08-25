# Arquivo: copiar_propostas.py (VERSÃO CORRIGIDA PARA BAIXAR TODOS OS ARQUIVOS)

import os
from gerenciador_sftp import GerenciadorSFTP
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS, CAMINHO_LOCAL_PROPOSTAS

def copiar_propostas_da_vps():
    """
    Automatiza o processo de baixar TODOS os arquivos da VPS
    para a pasta local definida no config.py.
    """
    print("--- INICIANDO SINCRONIZAÇÃO DE PROPOSTAS DA VPS ---")
    
    pasta_local = CAMINHO_LOCAL_PROPOSTAS
    if not pasta_local:
        print("🚨 ERRO: CAMINHO_LOCAL_PROPOSTAS não está definido em seu config.py/.env.")
        return False

    # Garante que a pasta de downloads local exista.
    if not os.path.exists(pasta_local):
        os.makedirs(pasta_local)
        print(f"✅ Pasta local '{pasta_local}' criada com sucesso.")

    try:
        # Usa 'with' para garantir que a conexão SFTP seja sempre fechada
        with GerenciadorSFTP(SSH_CONFIG) as sftp:
            print(f"🌐 Conectado ao VPS. Buscando arquivos em: {CAMINHO_REMOTO_PDFS}")
            
            # --- CORREÇÃO: Chama a função que lista TODOS os arquivos ---
            arquivos_para_baixar = sftp.listar_arquivos(CAMINHO_REMOTO_PDFS)

            if not arquivos_para_baixar:
                print("ℹ️ Nenhum arquivo novo encontrado no servidor para baixar.")
                return True

            print(f"✅ Encontrados {len(arquivos_para_baixar)} arquivos para baixar.")

            for nome_arquivo in arquivos_para_baixar:
                caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_arquivo}"
                caminho_local_completo = os.path.join(pasta_local, nome_arquivo)
                
                # Verifica se o arquivo já existe localmente para não baixá-lo de novo
                if os.path.exists(caminho_local_completo):
                    print(f"🔄 Arquivo '{nome_arquivo}' já existe localmente. Pulando.")
                    continue
                
                print(f"⬇️  Baixando '{nome_arquivo}'...")
                sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)

        print("\n--- SINCRONIZAÇÃO FINALIZADA COM SUCESSO ---")
        return True
    
    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado durante a sincronização: {e}")
        return False


if __name__ == "__main__":
    copiar_propostas_da_vps()