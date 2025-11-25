# Arquivo: main.py (VERSÃO FINAL COM RENOMEAÇÃO PARA UNICIDADE, LIMPEZA E FLUXO CORRIGIDO E ATUALIZAÇÃO NO BANCO)

import os
import glob
import shutil
import time
import re
from datetime import datetime
from typing import Tuple, Dict
from PIL import Image
# Importações necessárias para o fluxo de sincronização e exclusão remota
from config import CAMINHO_LOCAL_PROPOSTAS, SSH_CONFIG, CAMINHO_REMOTO_PDFS
from gerenciador_sftp import GerenciadorSFTP
from agger import conectar_e_abrir_prospeccao
# --- ALTERAÇÃO AQUI: Importando a nova função de atualização ---
from banco import buscar_cliente, atualizar_data_prospectada 
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
    Recebe uma lista de arquivos de um cliente, cria cópias renomeadas (adicionando a extensão
    ao nome base para unicidade no Agger) e retorna as listas de caminhos.

    Returns:
        Tuple[list, list]:
            - Lista de caminhos dos arquivos RENOMEADOS (para anexar).
            - Lista de caminhos dos arquivos ORIGINAIS (para mover/deletar da VPS).
    """
    arquivos_para_anexar_renomeados = []
    arquivos_para_mover_e_deletar_remotamente = [] 

    VALID_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    for caminho_arquivo_original in arquivos_originais:
        nome_arquivo_original = os.path.basename(caminho_arquivo_original)
        nome_base, extensao = os.path.splitext(nome_arquivo_original)
        
        if extensao.lower() in VALID_EXTENSIONS:
            
            # 1. Cria o novo nome único: Adiciona a extensão (em maiúsculas) entre parênteses.
            extensao_formatada = extensao.upper().replace('.', '')
            novo_nome_arquivo = f"{nome_base} ({extensao_formatada}){extensao.lower()}"
            # Cria a cópia renomeada na pasta LOCAL_PROPOSTAS
            caminho_arquivo_renomeado = os.path.join(CAMINHO_LOCAL_PROPOSTAS, novo_nome_arquivo)

            # 2. Copia/renomeia o arquivo
            try:
                if os.path.exists(caminho_arquivo_renomeado):
                    os.remove(caminho_arquivo_renomeado) # Garante que a cópia antiga seja apagada
                
                # shutil.copy2 é usado para manter metadados e é mais robusto
                shutil.copy2(caminho_arquivo_original, caminho_arquivo_renomeado)
                print(f"ℹ️  Arquivo renomeado para anexar: '{novo_nome_arquivo}'")

                arquivos_para_anexar_renomeados.append(caminho_arquivo_renomeado)
                # O caminho ORIGINAL precisa ser movido para 'processados' e deletado da VPS
                arquivos_para_mover_e_deletar_remotamente.append(caminho_arquivo_original)

            except Exception as e:
                print(f"🚨 ERRO ao renomear/copiar o arquivo '{nome_arquivo_original}': {e}")
                continue 
        else:
            print(f"⚠️  Arquivo '{nome_arquivo_original}' ignorado (não é PDF nem imagem suportada).")

    return arquivos_para_anexar_renomeados, arquivos_para_mover_e_deletar_remotamente

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

    # Mapeia clientes para agregá-los pelo nome base (ID + NOME_CLIENTE)
    clientes_a_processar: Dict[str, list] = {}
    for caminho_arquivo in lista_de_arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        # Extrai o ID (Grupo 1) e o NOME BASE (Grupo 2), ignorando o sufixo numérico opcional.
        match = re.match(r'^(\d+)\s+(.*?)(?:[\s_]\d+)?\..*$', nome_arquivo)

        if match:
            client_id = match.group(1).strip()
            nome_cliente_base = match.group(2).strip()
            
            # A chave única de agrupamento é ID + Nome Base (Ex: '712 MIGUEL FERREIRA')
            chave_unica = f"{client_id} {nome_cliente_base}" 
            # O nome para a busca no banco é apenas o nome base
            nome_cliente_para_busca = nome_cliente_base
            
            # Se a chave única (ID + Nome Base) não existe, cria a lista e armazena o nome para a busca no índice 0
            if chave_unica not in clientes_a_processar:
                clientes_a_processar[chave_unica] = [nome_cliente_para_busca]
            
            # Adiciona o caminho completo do arquivo à lista do grupo
            clientes_a_processar[chave_unica].append(caminho_arquivo)
    
    print(f"\n✅ {len(lista_de_arquivos)} arquivo(s) encontrado(s), correspondendo a {len(clientes_a_processar)} cliente(s) único(s) (por ID+Nome Base). Iniciando processamento...")

    # Itera sobre as chaves únicas (ID NOME_CLIENTE...)
    for chave_unica, arquivos_do_grupo in clientes_a_processar.items():
        # O nome do cliente para busca no banco está sempre na primeira posição
        nome_base_cliente = arquivos_do_grupo[0]
        arquivos_originais = arquivos_do_grupo[1:] # O resto são os caminhos dos arquivos
        
        # Extrai o ID do cliente da chave
        client_id_str = chave_unica.split(" ", 1)[0]
        client_id = int(client_id_str) if client_id_str.isdigit() else None

        dados_cliente = None
        try:
            print(f"\n▶️  Processando o grupo: {chave_unica}")
            
            # Busca os dados do cliente no banco (usando APENAS o nome base)
            dados_cliente = buscar_cliente(nome_base_cliente)

            if not dados_cliente:
                print(f"⚠️  Cliente '{nome_base_cliente}' não encontrado no banco de dados. Pulando.")
                registrar_log(chave_unica, "CLIENTE NÃO ENCONTRADO NO BANCO")
                continue
            
            if not dados_cliente.get('id'):
                print(f"🚨 ERRO: ID do cliente '{nome_base_cliente}' não encontrado nos dados do banco. Pulando.")
                registrar_log(chave_unica, "ID DO CLIENTE AUSENTE NO BANCO")
                continue

            # Prepara os anexos (cria cópias renomeadas)
            arquivos_para_anexar, arquivos_para_mover_e_deletar_remotamente = preparar_anexos_do_cliente(
                client_id, nome_base_cliente, arquivos_originais
            )
            
            if not arquivos_para_anexar:
                print(f"❌ Nenhum arquivo válido encontrado para '{chave_unica}'.")
                registrar_log(chave_unica, "NENHUM ANEXO VÁLIDO")
                continue
            
            # Adiciona a lista de arquivos renomeados ao dicionário do cliente para o preenchimento
            dados_cliente['anexos'] = arquivos_para_anexar

            conectar_e_abrir_prospeccao()
            sucesso = preencher_todos(dados_cliente)
            
            if sucesso:
                print(f"✅ Automação para '{chave_unica}' concluída com sucesso.")
                registrar_log(chave_unica, "SUCESSO", dados_cliente.get('vendedor', 'N/A'))
                
                # --- NOVO PASSO: ATUALIZAR DATA NO BANCO ---
                registro_id = dados_cliente.get('id')
                atualizar_data_prospectada(registro_id) # CHAMADA PARA A NOVA FUNÇÃO
                # ------------------------------------------
                
                # 1. Processa a movimentação local E a exclusão remota dos arquivos ORIGINAIS
                for arquivo_local_original in arquivos_para_mover_e_deletar_remotamente:
                    if not os.path.exists(arquivo_local_original): continue
                    
                    nome_do_arquivo_original = os.path.basename(arquivo_local_original)
                    destino_final = os.path.join(pasta_processados, nome_do_arquivo_original)
                    caminho_remoto_completo = f"{CAMINHO_REMOTO_PDFS}/{nome_do_arquivo_original}"

                    try:
                        # Movimentação Local (Arquivos ORIGINAIS): Força a substituição
                        if os.path.exists(destino_final):
                            os.remove(destino_final)
                        
                        shutil.move(arquivo_local_original, destino_final)
                        print(f"✔️  Arquivo original movido para 'processados': {nome_do_arquivo_original}")
                        
                        # Remoção da VPS
                        with GerenciadorSFTP(SSH_CONFIG) as sftp:
                            sftp.remover_arquivo_remoto(caminho_remoto_completo)
                            print(f"✔️  Arquivo original removido do VPS: {nome_do_arquivo_original}")

                    except Exception as e:
                        print(f"🚨 Falha ao mover/remover o arquivo '{nome_do_arquivo_original}'. Erro: {e}")

                # 2. Limpa os arquivos RENOMEADOS TEMPORÁRIOS
                for arquivo_renomeado in arquivos_para_anexar:
                    if os.path.exists(arquivo_renomeado):
                        try:
                            os.remove(arquivo_renomeado)
                            print(f"🗑️  Arquivo temporário deletado: {os.path.basename(arquivo_renomeado)}")
                        except Exception as e:
                            print(f"🚨 Falha ao deletar arquivo temporário '{os.path.basename(arquivo_renomeado)}': {e}")

            else:
                print(f"❌ Automação para '{chave_unica}' falhou.")
                registrar_log(chave_unica, "FALHA NO PREENCHIMENTO", dados_cliente.get('vendedor', 'N/A'))
        except Exception as e:
            print(f"🚨 Ocorreu um erro inesperado ao processar '{chave_unica}': {e}")
            vendedor = dados_cliente.get('vendedor', 'N/A') if dados_cliente else 'N/A'
            registrar_log(chave_unica, f"ERRO INESPERADO ({e})", vendedor)
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