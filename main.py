# Arquivo: main.py (VERSÃO FINAL PARA USAR ARQUIVOS LOCAIS)

import os
import glob
import shutil
from config import CAMINHO_LOCAL_PROPOSTAS # Importa a configuração da pasta local
from agger import conectar_e_abrir_prospeccao
from banco import buscar_cliente
from preencher.preencher import executar_preenchimento as preencher_todos

def processar_propostas_locais():
    """
    Função principal que orquestra o processo lendo PDFs de uma pasta local.
    """
    
    # 1. DEFINIR PASTA DE PROCESSADOS
    # Para manter tudo organizado, os PDFs processados com sucesso serão movidos para esta subpasta.
    pasta_processados = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "processados")
    if not os.path.exists(pasta_processados):
        print(f"📂 Criando pasta para arquivos processados em: {pasta_processados}")
        os.makedirs(pasta_processados)

    # 2. BUSCAR PDFs NA PASTA LOCAL
    # Usamos glob para encontrar todos os arquivos que terminam com .pdf na pasta especificada.
    print(f"🔎 Buscando PDFs na pasta local: {CAMINHO_LOCAL_PROPOSTAS}")
    caminho_de_busca = os.path.join(CAMINHO_LOCAL_PROPOSTAS, "*.pdf")
    lista_de_pdfs = glob.glob(caminho_de_busca)

    if not lista_de_pdfs:
        print("❌ Nenhum PDF encontrado na pasta local para processar.")
        return

    print(f"✅ {len(lista_de_pdfs)} PDF(s) encontrado(s). Iniciando processamento...")

    # Abre a prospecção uma única vez antes de começar o loop
    conectar_e_abrir_prospeccao()

    # 3. PROCESSAR CADA PDF ENCONTRADO
    # O 'for' loop vai passar por cada caminho de PDF encontrado.
    for caminho_local_completo in lista_de_pdfs:
        try:
            nome_do_pdf = os.path.basename(caminho_local_completo)
            print(f"\n▶️  Processando o arquivo: {nome_do_pdf}")

            # Extrai o nome do cliente do nome do arquivo (sem a extensão .pdf)
            nome_base_cliente = os.path.splitext(nome_do_pdf)[0]
            
            # Busca os dados do cliente no banco de dados
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando para o próximo.")
                continue # Pula para o próximo PDF do loop

            # A função de preenchimento recebe os dados e o NOME do arquivo.
            sucesso = preencher_todos(dados_cliente, nome_do_pdf)
            
            if sucesso:
                print(f"✅ Automação para '{nome_do_pdf}' concluída com sucesso.")
                # Move o arquivo local para a pasta 'processados'
                shutil.move(caminho_local_completo, pasta_processados)
                print(f"✔️  Arquivo movido para: {pasta_processados}")
            else:
                print(f"❌ Automação para '{nome_do_pdf}' falhou. O arquivo será mantido na pasta original.")

        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{nome_do_pdf}': {e}")
            # Continua para o próximo arquivo mesmo se um der erro
            continue

    print("\n🎉 Processamento de todos os arquivos concluído.")


if __name__ == "__main__":
    processar_propostas_locais()