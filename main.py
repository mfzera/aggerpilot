# Arquivo: main.py (VERSÃO CORRIGIDA PARA ANEXO SIMPLIFICADO)

import os
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
# A importação continua a mesma
from preencher.preencher import executar_preenchimento as preencher_todos 

def processar_proposta():
    """Função principal que orquestra todo o processo."""
    
    # Usa 'with' para garantir que a conexão SFTP seja aberta e fechada automaticamente
    with GerenciadorSFTP(SSH_CONFIG) as sftp:
        
        print(f"🔎 Buscando PDFs em: {CAMINHO_REMOTO_PDFS}")
        pdfs_remotos = sftp.listar_pdfs(CAMINHO_REMOTO_PDFS)

        if not pdfs_remotos:
            print("❌ Nenhum PDF encontrado no servidor.")
            return

        primeiro_pdf = pdfs_remotos[0]
        caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{primeiro_pdf}"
        print(f"▶️ Processando o arquivo: {primeiro_pdf}")

        # O caminho local agora é definido dentro do módulo 'anexar'
        # Mas ainda precisamos baixar o arquivo para algum lugar.
        # Vamos usar a pasta de downloads definida em 'anexar.py'
        # (Idealmente, essa pasta também estaria no config.py)
        try:
            from preencher.anexar import PASTA_PROPOSTAS_LOCAL
            caminho_local_completo = os.path.join(PASTA_PROPOSTAS_LOCAL, primeiro_pdf)
        except ImportError:
            print("🚨 ERRO: Não foi possível importar 'PASTA_PROPOSTAS_LOCAL' do módulo 'anexar.py'.")
            print("   -> Verifique se o arquivo 'preencher/anexar.py' existe e contém a constante.")
            return


        try:
            sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_completo)
            
            nome_base_cliente = os.path.splitext(primeiro_pdf)[0]
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                return

            conectar_e_abrir_prospeccao()
            
            # A chamada agora passa o dicionário de dados E apenas o NOME do arquivo PDF
            sucesso = preencher_todos(dados_cliente, primeiro_pdf)
            
            if sucesso:
                print("✅ Automação (preenchimento e anexo) concluída com sucesso.")
                # sftp.remover_arquivo_remoto(caminho_remoto_completo)
                print(f"✅ Arquivo '{primeiro_pdf}' foi processado e MANTIDO no servidor.")

            else:
                print("❌ Automação falhou. O arquivo não foi processado completamente.")

        except Exception as e:
            print(f"🚨 Ocorreu um erro durante o processamento no main: {e}")
        finally:
            # Garante que o arquivo local seja sempre deletado
            if 'caminho_local_completo' in locals() and os.path.exists(caminho_local_completo):
                os.remove(caminho_local_completo)
                print(f"🧹 Arquivo local '{caminho_local_completo}' removido.")

if __name__ == "__main__":
    processar_proposta()
