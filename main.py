# Arquivo: main.py (VERSÃO COM NOVO FLUXO)

import os
import glob
import shutil
import time
import re
from datetime import datetime
from typing import Tuple, Dict
from PIL import Image
from config import CAMINHO_LOCAL_PROPOSTAS
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
from preencher.preencher import executar_preenchimento as preencher_todos
from copiar_propostas import copiar_propostas_da_vps

def registrar_log(nome_cliente, status, vendedor="N/A"):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha_log = f"{nome_cliente} - {status} - ({timestamp}) - ({vendedor})\n"
    try:
        with open("automacao_log.txt", "a", encoding="utf-8") as f:
            f.write(linha_log)
    except Exception as e:
        print(f"🚨 Alerta: Falha ao escrever no arquivo de log. Erro: {e}")

def preparar_anexos_do_cliente(client_id: int, nome_base_cliente: str, arquivos_originais: list) -> Tuple[list, list]:
    """
    Recebe uma lista de arquivos de um cliente, converte imagens para PDF
    e retorna uma lista final de PDFs e uma lista de imagens originais para limpeza.
    Os arquivos já devem estar no padrão 'ID NOME_CLIENTE...'.
    """
    pdfs_finais = []
    imagens_originais = []
    
    for caminho_arquivo in arquivos_originais:
        nome_base_original, extensao = os.path.splitext(os.path.basename(caminho_arquivo))
        
        # Se for PDF, já adiciona na lista final
        if extensao.lower() == '.pdf':
            pdfs_finais.append(caminho_arquivo)
            continue

        # Se for imagem, converte para PDF mantendo o nome base
        if extensao.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            imagens_originais.append(caminho_arquivo)
            print(f"ℹ️  Imagem encontrada: '{os.path.basename(caminho_arquivo)}'. Convertendo para PDF...")
            try:
                imagem = Image.open(caminho_arquivo)
                if imagem.mode == 'RGBA':
                    imagem = imagem.convert('RGB')
                
                caminho_pdf_convertido = os.path.join(CAMINHO_LOCAL_PROPOSTAS, nome_base_original + ".pdf")
                imagem.save(caminho_pdf_convertido, "PDF", resolution=100.0)
                
                pdfs_finais.append(caminho_pdf_convertido)
                print(f"✅ Convertido para: '{os.path.basename(caminho_pdf_convertido)}'")
            except Exception as e:
                print(f"🚨 ERRO ao converter a imagem '{os.path.basename(caminho_arquivo)}': {e}")
        else:
            print(f"⚠️  Arquivo '{os.path.basename(caminho_arquivo)}' ignorado (não é PDF nem imagem suportada).")

    return pdfs_finais, imagens_originais

def processar_propostas_locais():
    print("Iniciando automação... Por favor, garanta que a janela do AGGER esteja no menu principal.")
    print("A automação começará em 5 segundos...")
    time.sleep(5)
    
    pasta_processados = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "processados")
    if not os.path.exists(pasta_processados):
        os.makedirs(pasta_processados)

    print(f"🔎 Buscando TODOS os arquivos na pasta local: {CAMINHO_LOCAL_PROPOSTAS}")
    caminho_de_busca = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "*.*")
    lista_de_arquivos = [f for f in glob.glob(caminho_de_busca) if os.path.isfile(f)]

    if not lista_de_arquivos:
        print("❌ Nenhum arquivo encontrado na pasta local para processar.")
        return

    # Mapeia clientes para agregá-los pelo nome base (sem ID e sufixos)
    clientes_a_processar: Dict[str, list] = {}
    for caminho_arquivo in lista_de_arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        # Extrai o nome do cliente do padrão "ID NOME ..."
        match = re.match(r'^\d+\s+(.*?)(?:\s+\d+)?\..*$', nome_arquivo)
        if match:
            nome_cliente = match.group(1).strip()
            if nome_cliente not in clientes_a_processar:
                clientes_a_processar[nome_cliente] = []
            clientes_a_processar[nome_cliente].append(caminho_arquivo)
    
    print(f"\n✅ {len(lista_de_arquivos)} arquivo(s) encontrado(s), correspondendo a {len(clientes_a_processar)} cliente(s) único(s). Iniciando processamento...")

    for nome_base_cliente, arquivos_do_cliente in clientes_a_processar.items():
        dados_cliente = None
        try:
            print(f"\n▶️  Processando o cliente: {nome_base_cliente}")
            
            # Busca os dados do cliente no banco
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando.")
                registrar_log(nome_base_cliente, "CLIENTE NÃO ENCONTRADO NO BANCO")
                continue
            
            client_id = dados_cliente.get('id')
            if not client_id:
                print(f"🚨 ERRO: ID do cliente '{nome_base_cliente}' não encontrado nos dados do banco. Pulando.")
                registrar_log(nome_base_cliente, "ID DO CLIENTE AUSENTE NO BANCO")
                continue

            # Prepara os anexos (basicamente converte imagens para PDF)
            pdfs_para_anexar, imagens_para_limpar = preparar_anexos_do_cliente(
                client_id, nome_base_cliente, arquivos_do_cliente
            )
            
            if not pdfs_para_anexar:
                print(f"❌ Nenhum arquivo PDF válido encontrado ou gerado para '{nome_base_cliente}'.")
                registrar_log(nome_base_cliente, "NENHUM ANEXO VÁLIDO")
                continue
            
            # Adiciona a lista de PDFs ao dicionário do cliente para o preenchimento
            dados_cliente['anexos'] = pdfs_para_anexar

            conectar_e_abrir_prospeccao()
            sucesso = preencher_todos(dados_cliente)
            
            if sucesso:
                print(f"✅ Automação para '{nome_base_cliente}' concluída com sucesso.")
                registrar_log(nome_base_cliente, "SUCESSO", dados_cliente.get('vendedor', 'N/A'))
                
                # Move todos os arquivos processados (PDFs e imagens originais)
                arquivos_a_mover = pdfs_para_anexar + imagens_para_limpar
                for arquivo_local in arquivos_a_mover:
                    if not os.path.exists(arquivo_local): continue
                    try:
                        shutil.move(arquivo_local, pasta_processados)
                    except Exception as e:
                        print(f"🚨 Falha ao mover o arquivo '{os.path.basename(arquivo_local)}'. Erro: {e}")
            else:
                print(f"❌ Automação para '{nome_base_cliente}' falhou.")
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
    if copiar_propostas_da_vps():
        print("\nPASSO 2: Iniciando o processamento das propostas...")
        processar_propostas_locais()
    else:
        print("\n❌ Processamento não iniciado devido a uma falha na sincronização.")