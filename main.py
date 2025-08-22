# Arquivo: main.py (VERSÃO FINAL COMPLETA E ATUALIZADA)

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
    agrupando por cliente, processando cada cliente uma única vez e limpando os arquivos.
    """
    
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

    # --- NOVA LÓGICA ---
    # 1. Montar uma lista de clientes únicos a partir dos nomes dos arquivos.
    # O uso de 'set' garante que não haverá nomes duplicados.
    clientes_unicos = set()
    for caminho_pdf in lista_de_pdfs:
        nome_arquivo = os.path.basename(caminho_pdf)
        # Remove a extensão .pdf
        nome_base_cliente = os.path.splitext(nome_arquivo)[0]
        # Uma forma simples de tratar "NOME 2", "NOME 3", etc.
        partes = nome_base_cliente.rsplit(' ', 1)
        if len(partes) > 1 and partes[1].isdigit():
            nome_base_cliente = partes[0]
        
        clientes_unicos.add(nome_base_cliente.strip())

    print(f"\n✅ {len(lista_de_pdfs)} PDF(s) encontrado(s), correspondendo a {len(clientes_unicos)} cliente(s) único(s). Iniciando processamento...")

    # 2. O loop principal agora é por cliente, não por arquivo.
    for nome_base_cliente in clientes_unicos:
        dados_cliente = None # Inicializa para garantir que a variável exista

        try:
            print(f"\n▶️  Processando o cliente: {nome_base_cliente}")

            # Busca os dados do cliente UMA VEZ. A função já trará a lista de todos os anexos.
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando para o próximo.")
                registrar_log(nome_base_cliente, "CLIENTE NÃO ENCONTRADO NO BANCO")
                continue

            # Conecta e abre a prospecção UMA VEZ por cliente.
            conectar_e_abrir_prospeccao()
            
            # A função preencher_todos agora só precisa dos dados do cliente,
            # pois a lista de anexos já está dentro de dados_cliente['anexos'].
            # LEMBRE-SE DE AJUSTAR A FUNÇÃO preencher_todos EM SEU ARQUIVO ORIGINAL.
            sucesso = preencher_todos(dados_cliente)
            
            # Encontra todos os arquivos PDF locais para este cliente para poder movê-los/removê-los
            arquivos_do_cliente_local = glob.glob(os.path.join(CAMINHO_LOCAL_PROPOSTAS, f"{nome_base_cliente}*.pdf"))
            
            if sucesso:
                print(f"✅ Automação para o cliente '{nome_base_cliente}' concluída com sucesso.")
                registrar_log(nome_base_cliente, "SUCESSO", dados_cliente.get('vendedor', 'N/A'))
                
                # Move e remove todos os arquivos associados
                for arquivo_local in arquivos_do_cliente_local:
                    nome_do_pdf = os.path.basename(arquivo_local)
                    try:
                        destino_final = os.path.join(pasta_processados, nome_do_pdf)
                        if os.path.exists(destino_final):
                            os.remove(destino_final)
                        shutil.move(arquivo_local, destino_final)
                        print(f"✔️  Arquivo local movido: {nome_do_pdf}")

                        caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_do_pdf}"
                        with GerenciadorSFTP(SSH_CONFIG) as sftp:
                            sftp.remover_arquivo_remoto(caminho_remoto_completo)
                        print(f"✔️  Arquivo removido do VPS: {nome_do_pdf}")
                    except Exception as e:
                        print(f"🚨 Falha ao mover/remover o arquivo '{nome_do_pdf}'. Erro: {e}")
            
            else:
                print(f"❌ Automação para o cliente '{nome_base_cliente}' falhou.")
                registrar_log(nome_base_cliente, "FALHA NO PREENCHIMENTO", dados_cliente.get('vendedor', 'N/A'))

        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{nome_base_cliente}': {e}")
            vendedor = dados_cliente.get('vendedor', 'N/A') if dados_cliente else 'N/A'
            registrar_log(nome_base_cliente, f"ERRO INESPERADO ({e})", vendedor)
            
        finally:
            print("---------------------------------------------------------")
            print("... Pausa de 3 segundos para estabilizar o AGGER ...")
            time.sleep(3) 

    print("\n🎉 Processamento de todos os clientes concluído.")


if __name__ == "__main__":
    print("PASSO 1: Sincronizando arquivos da VPS...")
    sucesso_copia = copiar_propostas_da_vps()

    if sucesso_copia:
        print("\nPASSO 2: Iniciando o processamento das propostas...")
        processar_propostas_locais()
    else:
        print("\n❌ O processamento não foi iniciado devido a uma falha na sincronização dos arquivos.")