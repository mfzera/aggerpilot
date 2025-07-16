import os
from gerenciador_sftp import GerenciadorSFTP
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS

# --- CONFIGURAÇÃO ---
# Defina aqui a pasta no seu computador onde as propostas serão salvas.
PASTA_LOCAL_DOWNLOADS = r"C:\Users\migue\Desktop\automação\propostas_vps"

def copiar_propostas_da_vps():
    """
    Automatiza o processo de baixar todas as propostas em PDF da VPS
    para uma pasta local.
    """
    print("--- INICIANDO AUTOMAÇÃO DE CÓPIA DE PROPOSTAS ---")
    
    # Garante que a pasta de downloads local exista.
    try:
        if not os.path.exists(PASTA_LOCAL_DOWNLOADS):
            os.makedirs(PASTA_LOCAL_DOWNLOADS)
            print(f"✅ Pasta local '{PASTA_LOCAL_DOWNLOADS}' criada com sucesso.")
    except Exception as e:
        print(f"🚨 ERRO: Não foi possível criar a pasta local '{PASTA_LOCAL_DOWNLOADS}'. Detalhe: {e}")
        return

    # Valida se todas as chaves SSH necessárias existem na configuração
    required_keys = ['hostname', 'port', 'username', 'password']
    if not all(key in SSH_CONFIG and SSH_CONFIG[key] is not None for key in required_keys):
        print("🚨 ERRO: A configuração SSH está incompleta. Verifique seu arquivo .env e config.py.")
        print(f"   -> Chaves necessárias: {required_keys}")
        print(f"   -> Chaves e valores encontrados: {SSH_CONFIG}")
        return

    # Instancia o gerenciador SFTP com as configurações
    # CORREÇÃO: Passando o dicionário SSH_CONFIG diretamente, como a classe espera.
    sftp_manager = GerenciadorSFTP(SSH_CONFIG)

    try:
        # Conecta ao servidor
        # A conexão agora é feita dentro do __enter__ ou chamando sftp_manager.conectar()
        sftp_manager.conectar()

        # Usa a variável CAMINHO_REMOTO_PDFS
        caminho_remoto = CAMINHO_REMOTO_PDFS
        if not caminho_remoto:
            print("🚨 ERRO: O caminho remoto para os PDFs não está definido. Verifique a variável REMOTO_PDFS no seu arquivo .env.")
            return

        # CORREÇÃO: Chamando o método correto 'listar_pdfs' da sua classe.
        arquivos_pdf = sftp_manager.listar_pdfs(caminho_remoto)

        if not arquivos_pdf:
            print(f"ℹ️ Nenhum arquivo PDF encontrado na pasta remota: {caminho_remoto}")
            return

        print(f"✅ Encontrados {len(arquivos_pdf)} arquivos PDF para baixar.")

        # Baixa cada arquivo encontrado
        for nome_arquivo in arquivos_pdf:
            caminho_remoto_completo = f"{caminho_remoto}/{nome_arquivo}"
            caminho_local_completo = os.path.join(PASTA_LOCAL_DOWNLOADS, nome_arquivo)
            
            print(f"\n⬇️  Baixando '{nome_arquivo}'...")
            try:
                sftp_manager.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)
            except Exception as e:
                print(f"   -> 🚨 Falha ao baixar '{nome_arquivo}'. Detalhe: {e}")

    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado durante a operação: {e}")
    finally:
        # Garante que a conexão seja sempre fechada
        sftp_manager.desconectar()
        print("\n--- AUTOMAÇÃO DE CÓPIA FINALIZADA ---")


if __name__ == "__main__":
    copiar_propostas_da_vps()
