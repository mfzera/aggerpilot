# Arquivo: main.py (CORRIGIDO PARA BUSCA DE CLIENTE COM ID NO NOME DO ARQUIVO)

import os
import glob
import shutil
import time
import re
from datetime import datetime
from typing import Tuple
from PIL import Image
from config import CAMINHO_LOCAL_PROPOSTAS, SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
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
    Os arquivos locais são renomeados para o padrão 'ID NOME_CLIENTE...'.
    """
    pdfs_finais = []
    imagens_originais = []

    # Novo prefixo para o arquivo: 'ID NOME_BASE_CLIENTE' (usa o nome LIMPO para o prefixo)
    novo_prefixo = f"{client_id} {nome_base_cliente}".strip()
    
    print(f"[INFO] Aplicando novo padrão de nome: '{novo_prefixo}...extensão'")


    for caminho_arquivo in arquivos_originais:
        nome_base_original, extensao = os.path.splitext(caminho_arquivo)
        
        # Remove a parte do nome base do cliente para isolar apenas o sufixo (ex: ' 1', '')
        # Se o arquivo for "2109 BARRY ALLEN 1.pdf", e nome_base_cliente for "BARRY ALLEN",
        # a substituição fará nome_base_original: "2109 BARRY ALLEN 1", sufixo_mantido: "2109 1"
        # O nome_base_cliente deve ser o nome LIMPO do cliente (sem o ID), mas o caminho_arquivo pode ter o ID.
        
        # É mais seguro buscar o nome base original do arquivo (sem extensão)
        nome_arquivo_sem_extensao = os.path.basename(nome_base_original)
        
        # 1. Tenta remover o ID prefixo do nome do arquivo (se houver)
        nome_sem_id_prefixo = nome_arquivo_sem_extensao
        match_id_prefixo = re.match(r'^\d+\s+', nome_arquivo_sem_extensao)
        if match_id_prefixo:
            nome_sem_id_prefixo = nome_arquivo_sem_extensao[match_id_prefixo.end():]
        
        # 2. Isola o sufixo (ex: " 1" de "BARRY ALLEN 1")
        # Substitui a primeira ocorrência do nome base do cliente (limpo) no nome do arquivo (sem o ID prefixo).
        sufixo_mantido = nome_sem_id_prefixo.replace(nome_base_cliente, '', 1).strip()
        
        # 3. Constrói o novo nome base completo: "ID NOME CLIENTE" + " SUFIXO"
        if sufixo_mantido:
            # Garante que o sufixo não é só números (que é a parte que deve ser limpa)
            if re.match(r'^\d+$', sufixo_mantido):
                # Se o sufixo for só números, é provavelmente o sufixo de cópia (ex: 1)
                novo_nome_base = f"{novo_prefixo} {sufixo_mantido}".strip()
            else:
                # Se for texto no sufixo (ex: "DOC CPF"), apenas apenda
                novo_nome_base = f"{novo_prefixo} {sufixo_mantido}".strip()
        else:
            novo_nome_base = novo_prefixo
            
        # Define o novo caminho completo, com a extensão original, e o caminho de destino do PDF
        novo_caminho_arquivo = os.path.join(CAMINHO_LOCAL_PROPOSTAS, novo_nome_base + extensao)
        caminho_pdf_convertido = os.path.join(CAMINHO_LOCAL_PROPOSTAS, novo_nome_base + ".pdf")

        # --- Renomear o arquivo original (se necessário) ---
        if caminho_arquivo != novo_caminho_arquivo:
            if os.path.exists(caminho_arquivo):
                try:
                    # Limpa o arquivo de destino se já existir
                    if os.path.exists(novo_caminho_arquivo): os.remove(novo_caminho_arquivo)
                    os.rename(caminho_arquivo, novo_caminho_arquivo)
                    print(f"  [RENAME] Arquivo original renomeado para: {os.path.basename(novo_caminho_arquivo)}")
                    # Atualiza o ponteiro de processamento para o novo caminho
                    caminho_arquivo = novo_caminho_arquivo
                except Exception as e:
                     print(f"🚨 ERRO ao renomear o arquivo '{os.path.basename(caminho_arquivo)}': {e}")
                     caminho_arquivo = novo_caminho_arquivo
            else:
                caminho_arquivo = novo_caminho_arquivo


        # --- Processar PDF existente ou converter imagem ---
        if extensao.lower() == '.pdf':
            pdfs_finais.append(caminho_arquivo)
            continue

        if extensao.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            imagens_originais.append(caminho_arquivo)
            print(f"[INFO] Imagem encontrada: '{os.path.basename(caminho_arquivo)}'. Convertendo para PDF...")
            try:
                imagem = Image.open(caminho_arquivo)
                if imagem.mode == 'RGBA':
                    imagem = imagem.convert('RGB')
                
                # Salva a conversão com o novo nome base (ID CLIENTE...)
                imagem.save(caminho_pdf_convertido, "PDF", resolution=100.0)
                
                pdfs_finais.append(caminho_pdf_convertido)
                print(f"[SUCESSO] Convertido para: '{os.path.basename(caminho_pdf_convertido)}'")
            except Exception as e:
                print(f"🚨 ERRO ao converter a imagem '{os.path.basename(caminho_arquivo)}': {e}")
        else:
            print(f"[AVISO] Arquivo '{os.path.basename(caminho_arquivo)}' ignorado (não é PDF nem imagem suportada).")

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

    clientes_unicos = set()
    for caminho_arquivo in lista_de_arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        # Lógica original para extrair o nome base do cliente:
        nome_base = os.path.splitext(nome_arquivo)[0] # Ex: "2109 BARRY ALLEN 1"
        nome_base_cliente = re.sub(r'\d+$', '', nome_base).strip() # Ex: "2109 BARRY ALLEN"
        clientes_unicos.add(nome_base_cliente)

    print(f"\n✅ {len(lista_de_arquivos)} arquivo(s) encontrado(s), correspondendo a {len(clientes_unicos)} cliente(s) único(s). Iniciando processamento...")

    # A variável 'nome_base_cliente_com_id' contém o nome extraído do arquivo (com o ID, ex: "2109 BARRY ALLEN")
    for nome_base_cliente_com_id in clientes_unicos:
        dados_cliente = None
        try:
            # --- CORREÇÃO APLICADA AQUI: LIMPA O NOME PARA A BUSCA NO BANCO ---
            nome_limpo_para_busca = nome_base_cliente_com_id
            # Verifica se a string começa com dígitos seguidos de um ou mais espaços
            match = re.match(r'^(\d+\s+)(.*)', nome_base_cliente_com_id)
            if match:
                 # match.group(2) é a parte do nome após o ID e espaço
                 nome_limpo_para_busca = match.group(2).strip()
            
            print(f"\n▶️  Processando o cliente: {nome_base_cliente_com_id} (Busca no BD por: {nome_limpo_para_busca})")
            
            # CHAMA A FUNÇÃO DE BUSCA COM O NOME LIMPO
            dados_cliente = buscar_cliente(nome_limpo_para_busca)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_limpo_para_busca}' não encontrado no banco de dados. Pulando para o próximo.")
                registrar_log(nome_limpo_para_busca, "CLIENTE NÃO ENCONTRADO NO BANCO")
                continue
            
            # Define o nome base do cliente (limpo) para ser usado nas chamadas subsequentes
            nome_base_cliente = nome_limpo_para_busca
            
            # --- OBTENDO O ID DO CLIENTE ---
            client_id = dados_cliente.get('id', 0)
            if not client_id:
                print(f"🚨 ERRO: ID do cliente '{nome_base_cliente}' não encontrado nos dados do banco. Pulando.")
                registrar_log(nome_base_cliente, "ID DO CLIENTE AUSENTE NO BANCO")
                continue


            # 1. Encontra os arquivos originais (usa o nome COM ID, pois é assim que estão na pasta local)
            arquivos_originais_do_cliente = glob.glob(os.path.join(CAMINHO_LOCAL_PROPOSTAS, f"{nome_base_cliente_com_id}*.*"))
            
            # 2. Prepara os anexos, renomeando-os para o formato ID NOME_CLIENTE... 
            # Note que a função usa o 'nome_base_cliente' (limpo) para criar o novo prefixo.
            pdfs_para_anexar, imagens_para_limpar = preparar_anexos_do_cliente(
                client_id, nome_base_cliente, arquivos_originais_do_cliente
            )
            
            if not pdfs_para_anexar:
                print(f"❌ Nenhum arquivo PDF válido encontrado ou gerado para o cliente '{nome_base_cliente}'.")
                registrar_log(nome_base_cliente, "NENHUM ANEXO VÁLIDO")
                continue
            
            # Adiciona a lista de PDFs ao dicionário do cliente
            dados_cliente['anexos'] = pdfs_para_anexar

            conectar_e_abrir_prospeccao()
            sucesso = preencher_todos(dados_cliente)
            
            if sucesso:
                print(f"✅ Automação para o cliente '{nome_base_cliente}' concluída com sucesso.")
                registrar_log(nome_base_cliente, "SUCESSO", dados_cliente.get('vendedor', 'N/A'))
                
                arquivos_a_mover = pdfs_para_anexar + imagens_para_limpar
                for arquivo_local in arquivos_a_mover:
                    if not os.path.exists(arquivo_local): continue
                    
                    nome_do_arquivo = os.path.basename(arquivo_local)
                    try:
                        destino_final = os.path.join(pasta_processados, nome_do_arquivo)
                        if os.path.exists(destino_final): os.remove(destino_final)
                        shutil.move(arquivo_local, destino_final)
                        print(f"✔️  Arquivo local movido: {nome_do_arquivo}")
                        
                        # --- Lógica para remover o arquivo original da VPS ---
                        # 1. Reverte o nome para o formato original (sem o ID prefixo)
                        prefixo_id_e_espaco = f"{client_id} "
                        if nome_do_arquivo.startswith(prefixo_id_e_espaco):
                             # Ex: "123 NOME.pdf" -> "NOME.pdf"
                             nome_original_vps_completo = nome_do_arquivo[len(prefixo_id_e_espaco):].strip()
                        else:
                             nome_original_vps_completo = nome_do_arquivo # Não deveria acontecer
                        
                        nome_base_remoto = os.path.splitext(nome_original_vps_completo)[0]

                        # 2. Busca e remove no VPS usando o nome original
                        with GerenciadorSFTP(SSH_CONFIG) as sftp:
                            arquivos_remotos = sftp.listar_arquivos(CAMINHO_REMOTO_PDFS)
                            for arq_remoto in arquivos_remotos:
                                # Procura arquivos no VPS que comecem com o nome base original (sem extensão)
                                if arq_remoto.startswith(nome_base_remoto):
                                    caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{arq_remoto}"
                                    sftp.remover_arquivo_remoto(caminho_remoto_completo)
                                    print(f"✔️  Arquivo removido do VPS: {arq_remoto}")
                                    break
                    except Exception as e:
                        print(f"🚨 Falha ao mover/remover o arquivo '{nome_do_arquivo}'. Erro: {e}")
            else:
                print(f"❌ Automação para o cliente '{nome_base_cliente}' falhou.")
                registrar_log(nome_base_cliente, "FALHA NO PREENCHIMENTO", dados_cliente.get('vendedor', 'N/A'))
        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{nome_base_cliente_com_id}': {e}")
            vendedor = dados_cliente.get('vendedor', 'N/A') if dados_cliente else 'N/A'
            registrar_log(nome_base_cliente_com_id, f"ERRO INESPERADO ({e})", vendedor)
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