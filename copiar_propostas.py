# Arquivo: copiar_propostas.py (VERSÃO SIMPLIFICADA)

import os
from gerenciador_sftp import GerenciadorSFTP
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS, CAMINHO_LOCAL_PROPOSTAS

def copiar_propostas_da_vps():
    """
    Baixa os arquivos da VPS que ainda não existem na pasta local,
    mantendo o nome original do arquivo.
    """
    print("--- INICIANDO SINCRONIZAÇÃO DE PROPOSTAS DA VPS ---")

    if not CAMINHO_LOCAL_PROPOSTAS:
        print("🚨 ERRO: CAMINHO_LOCAL_PROPOSTAS não está definido em seu config.py/.env.")
        return False

    if not os.path.exists(CAMINHO_LOCAL_PROPOSTAS):
        os.makedirs(CAMINHO_LOCAL_PROPOSTAS)
        print(f"✅ Pasta local '{CAMINHO_LOCAL_PROPOSTAS}' criada com sucesso.")

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
                caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_arquivo_remoto}"
                caminho_local_completo = os.path.join(CAMINHO_LOCAL_PROPOSTAS, nome_arquivo_remoto)

                if os.path.exists(caminho_local_completo):
                    #print(f"🔄 Arquivo '{nome_arquivo_remoto}' já existe localmente. Pulando.")
                    continue
                
                print(f"⬇️  Baixando '{nome_arquivo_remoto}'...")
                sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)
                arquivos_baixados += 1

        print(f"\n--- SINCRONIZAÇÃO FINALIZADA. {arquivos_baixados} NOVOS ARQUIVOS BAIXADOS ---")
        return True
    
    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado durante a sincronização: {e}")
        return False