# Arquivo: main.py (VERSÃO MODIFICADA PARA NÃO DELETAR O PDF)

import os
from config import SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
# As importações abaixo podem variar dependendo da sua estrutura final
# Vou usar as que estavam no seu código.
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
# Supondo que 'preencher_todos' venha de um módulo 'preencher'
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
        # Monta o caminho completo do arquivo no servidor
        caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{primeiro_pdf}"
        print(f"▶️ Processando o arquivo: {primeiro_pdf}")

        # Define um caminho local temporário para onde o arquivo será baixado
        caminho_local_temporario = os.path.join(os.getcwd(), primeiro_pdf)

        try:
            # Baixa o PDF para o computador local temporariamente
            sftp.baixar_arquivo(caminho_remoto_completo, caminho_local_temporario)
            
            # Extrai o nome do cliente do nome do arquivo PDF (Ex: "Miguel.pdf" -> "Miguel")
            nome_base_cliente = os.path.splitext(primeiro_pdf)[0]

            # Chama a função buscar_cliente PASSANDO o nome que descobrimos
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                # A mensagem de erro já é impressa pela função buscar_cliente, então só saímos
                return

            # NOTA: A automação com PyAutoGUI não precisa da 'janela' retornada aqui
            conectar_e_abrir_prospeccao()
            # A função de preenchimento do PyAutoGUI é chamada aqui
            sucesso = preencher_todos(dados_cliente)
            
            if sucesso:
                print("✅ Automação concluída com sucesso.")
                
                # --- ALTERAÇÃO AQUI ---
                # A linha abaixo foi comentada para NÃO apagar mais o PDF do servidor.
                # sftp.remover_arquivo_remoto(caminho_remoto_completo)
                print(f"✅ Arquivo '{primeiro_pdf}' foi processado e MANTIDO no servidor.")

            else:
                print("❌ Automação falhou. O arquivo não foi processado completamente.")


        except Exception as e:
            print(f"🚨 Ocorreu um erro durante o processamento no main: {e}")
        finally:
            # Garante que o arquivo local temporário seja sempre deletado, mesmo se der erro
            if os.path.exists(caminho_local_temporario):
                os.remove(caminho_local_temporario)
                print(f"🧹 Arquivo local temporário '{caminho_local_temporario}' removido.")

# Executa a função principal quando o script é chamado
if __name__ == "__main__":
    processar_proposta()