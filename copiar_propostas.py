# Arquivo: copiar_propostas.py (VERSÃO MELHORADA PARA SER USADO COMO MÓDULO)

import os
from gerenciador_sftp import GerenciadorSFTP
# --- MUDANÇA: Agora importa também o caminho local do config.py ---
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS, CAMINHO_LOCAL_PROPOSTAS

def copiar_propostas_da_vps():
    """
    Automatiza o processo de baixar todas as propostas em PDF da VPS
    para a pasta local definida no config.py.
    """
    print("--- INICIANDO SINCRONIZAÇÃO DE PROPOSTAS DA VPS ---")
    
    # --- MUDANÇA: Usa a variável do config.py em vez de uma local ---
    pasta_local = CAMINHO_LOCAL_PROPOSTAS
    if not pasta_local:
        print("🚨 ERRO: CAMINHO_LOCAL_PROPOSTAS não está definido em seu config.py/.env.")
        return False # Retorna False em caso de falha

    # Garante que a pasta de downloads local exista.
    if not os.path.exists(pasta_local):
        os.makedirs(pasta_local)
        print(f"✅ Pasta local '{pasta_local}' criada com sucesso.")

    try:
        # Usa 'with' para garantir que a conexão SFTP seja sempre fechada
        with GerenciadorSFTP(SSH_CONFIG) as sftp:
            print(f"🌐 Conectado ao VPS. Buscando arquivos em: {CAMINHO_REMOTO_PDFS}")
            arquivos_pdf = sftp.listar_pdfs(CAMINHO_REMOTO_PDFS)

            if not arquivos_pdf:
                print("ℹ️ Nenhum arquivo PDF novo encontrado no servidor para baixar.")
                return True # Não é um erro, apenas não há nada a fazer

            print(f"✅ Encontrados {len(arquivos_pdf)} arquivos PDF para baixar.")

            for nome_arquivo in arquivos_pdf:
                caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_arquivo}"
                caminho_local_completo = os.path.join(pasta_local, nome_arquivo)
                
                # Verifica se o arquivo já existe localmente para não baixá-lo de novo
                if os.path.exists(caminho_local_completo):
                    print(f"🔄 Arquivo '{nome_arquivo}' já existe localmente. Pulando.")
                    continue
                
                print(f"⬇️  Baixando '{nome_arquivo}'...")
                sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)

        print("--- SINCRONIZAÇÃO FINALIZADA COM SUCESSO ---")
        return True # Retorna True em caso de sucesso
    
    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado durante a sincronização: {e}")
        return False # Retorna False em caso de falha


if __name__ == "__main__":
    copiar_propostas_da_vps()