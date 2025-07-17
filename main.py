# Arquivo: main.py (VERSÃO FINAL COMPLETA)

import os
import glob
import shutil
import time
from datetime import datetime
from config import CAMINHO_LOCAL_PROPOSTAS, SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
from preencher.preencher import executar_preenchimento as preencher_todos
from copiar_propostas import copiar_propostas_da_vps

def registrar_log(nome_cliente, status, vendedor="N/A"):
    """
    Registra uma linha de log em um arquivo .txt.
    """
    # Formata a data e hora atuais
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Monta a linha de log no formato desejado
    linha_log = f"{nome_cliente} - {status} - ({timestamp}) - ({vendedor})\n"
    
    try:
        # Abre o arquivo em modo 'append' (a), que adiciona ao final sem apagar o conteúdo
        # 'encoding="utf-8"' garante o suporte a caracteres especiais
        with open("automacao_log.txt", "a", encoding="utf-8") as f:
            f.write(linha_log)
    except Exception as e:
        print(f"🚨 Alerta: Falha ao escrever no arquivo de log. Erro: {e}")


def processar_propostas_locais():
    """
    Função principal que orquestra o processo lendo PDFs de uma pasta local,
    processando-os e limpando os arquivos originais.
    """
    
    # Adiciona uma pausa inicial para o usuário focar na janela do AGGER
    print("Iniciando automação... Por favor, garanta que a janela do AGGER esteja no menu principal.")
    print("A automação começará em 5 segundos...")
    time.sleep(5)
    
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
        nome_base_cliente = os.path.splitext(nome_do_pdf)[0]
        dados_cliente = None # Inicializa para garantir que a variável exista

        try:
            print(f"\n▶️  Processando o arquivo: {nome_do_pdf}")
            conectar_e_abrir_prospeccao()

            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando para o próximo.")
                registrar_log(nome_base_cliente, "CLIENTE NÃO ENCONTRADO NO BANCO")
                continue

            sucesso = preencher_todos(dados_cliente, nome_do_pdf)
            
            if sucesso:
                print(f"✅ Automação para '{nome_do_pdf}' concluída com sucesso.")
                registrar_log(nome_base_cliente, "SUCESSO", dados_cliente.get('vendedor', 'N/A'))
                
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
                registrar_log(nome_base_cliente, "FALHA NO PREENCHIMENTO", dados_cliente.get('vendedor', 'N/A'))

        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{nome_do_pdf}': {e}")
            vendedor = dados_cliente.get('vendedor', 'N/A') if dados_cliente else 'N/A'
            registrar_log(nome_base_cliente, f"ERRO INESPERADO ({e})", vendedor)
            
        finally:
            print("---------------------------------------------------------")
            print("... Pausa de 3 segundos para estabilizar o AGGER ...")
            time.sleep(3) 

    print("\n🎉 Processamento de todos os arquivos concluído.")


if __name__ == "__main__":
    print("PASSO 1: Sincronizando arquivos da VPS...")
    sucesso_copia = copiar_propostas_da_vps()

    if sucesso_copia:
        print("\nPASSO 2: Iniciando o processamento das propostas...")
        processar_propostas_locais()
    else:
        print("\n❌ O processamento não foi iniciado devido a uma falha na sincronização dos arquivos.")
