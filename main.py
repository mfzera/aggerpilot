# Arquivo: main.py (VERSÃO COM PAUSA DE ESTABILIZAÇÃO)

import os
import glob
import shutil
import time # <-- MUDANÇA: Importa a biblioteca 'time'
from config import CAMINHO_LOCAL_PROPOSTAS, SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
from preencher.preencher import executar_preenchimento as preencher_todos
from copiar_propostas import copiar_propostas_da_vps

def processar_propostas_locais():
    # ... (o início da função continua igual) ...
    pasta_processados = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "processados")
    if not os.path.exists(pasta_processados):
        os.makedirs(pasta_processados)

    print(f"🔎 Buscando PDFs na pasta local: {CAMINHO_LOCAL_PROPOSTAS}")
    caminho_de_busca = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "*.pdf")
    lista_de_pdfs = glob.glob(caminho_de_busca)

    if not lista_de_pdfs:
        print("❌ Nenhum PDF encontrado na pasta local para processar.")
        return

    print(f"\n✅ {len(lista_de_pdfs)} PDF(s) encontrado(s). Iniciando processamento...")

    for caminho_local_completo in lista_de_pdfs:
        nome_do_pdf = os.path.basename(caminho_local_completo)
        try:
            print(f"\n▶️  Processando o arquivo: {nome_do_pdf}")

            conectar_e_abrir_prospeccao()

            nome_base_cliente = os.path.splitext(nome_do_pdf)[0]
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando para o próximo.")
                continue # <-- Este 'continue' pula para a pausa no final do loop

            sucesso = preencher_todos(dados_cliente, nome_do_pdf)
            
            if sucesso:
                print(f"✅ Automação para '{nome_do_pdf}' concluída com sucesso.")
                
                try:
                    destino_final = os.path.join(pasta_processados, nome_do_pdf)
                    if os.path.exists(destino_final):
                        print(f"⚠️  Arquivo '{nome_do_pdf}' já existia em 'processados'. O arquivo antigo será substituído.")
                        os.remove(destino_final)
                    shutil.move(caminho_local_completo, destino_final)
                    print(f"✔️  Arquivo local movido para: {pasta_processados}")
                except Exception as e:
                    print(f"🚨 Falha ao mover o arquivo local '{nome_do_pdf}'. Erro: {e}")

                try:
                    caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_do_pdf}"
                    print(f"🌐 Conectando ao VPS para remover o arquivo '{nome_do_pdf}'...")
                    with GerenciadorSFTP(SSH_CONFIG) as sftp:
                        sftp.remover_arquivo_remoto(caminho_remoto_completo)
                    print(f"✔️  Arquivo '{nome_do_pdf}' também foi removido do servidor VPS.")
                except Exception as e:
                    print(f"⚠️  AVISO: Falha ao remover '{nome_do_pdf}' do VPS. Erro: {e}")
            
            else:
                print(f"❌ Automação para '{nome_do_pdf}' falhou.")

        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{nome_do_pdf}': {e}")
            # Mesmo em caso de erro, o script continua e fará a pausa
            
        finally:
            # --- NOVA MUDANÇA ---
            # Pausa de 3 segundos no final de CADA iteração para estabilizar a aplicação.
            print("---------------------------------------------------------")
            print("... Pausa de 3 segundos para estabilizar o AGGER ...")
            time.sleep(3) 
            # --- FIM DA NOVA MUDANÇA ---

    print("\n🎉 Processamento de todos os arquivos concluído.")


if __name__ == "__main__":
    print("PASSO 1: Sincronizando arquivos da VPS...")
    sucesso_copia = copiar_propostas_da_vps()

    if sucesso_copia:
        print("\nPASSO 2: Iniciando o processamento das propostas...")
        processar_propostas_locais()
    else:
        print("\n❌ O processamento não foi iniciado devido a uma falha na sincronização dos arquivos.")