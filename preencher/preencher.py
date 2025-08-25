# Arquivo: preencher/preencher.py (VERSÃO CORRIGIDA E MAIS ROBUSTA)

import pyautogui
import time
import os
from pywinauto import Application # Importa a Application para esperas inteligentes

# --- CORREÇÃO: As importações agora são feitas de módulos específicos ---
from .nome import preencher as preencher_nome
from .telefone import preencher as preencher_telefone
from .item import preencher as preencher_item
from .vencimento import preencher as preencher_vencimento
from .sair_em_renovacoes import selecionar as selecionar_sair_em_renovacoes
from .observacoes import preencher as preencher_observacoes
from .criar_tarefa import selecionar as selecionar_criar_tarefa
from .responsavel import selecionar_responsavel
from .vendedor import selecionar as selecionar_vendedor
from .status import selecionar as selecionar_status
from .anexar import anexar as anexar_arquivos 
from .salvar import salvar_prospeccao

APP_TITLE = "AGGER GESTOR"

def esperar_agger_ficar_ocioso():
    """Função auxiliar para esperar a CPU do Agger baixar, indicando que ele está pronto."""
    try:
        print("[INFO] Aguardando o Agger ficar ocioso...")
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=15)
        # Espera o processo do app ter baixo uso de CPU por um tempo
        app.wait_cpu_usage_lower(threshold=5, timeout=30, usage_interval=1.0)
        print("[INFO] Agger está pronto para a próxima ação.")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível esperar o Agger ficar ocioso. Erro: {e}")
        time.sleep(2) # Usa uma pausa fixa como alternativa

def executar_preenchimento(dados_cliente: dict) -> bool:
    """
    Orquestra o preenchimento, usando esperas inteligentes para maior estabilidade.
    """
    try:
        print("Iniciando o preenchimento final com a sequência mapeada...")
        time.sleep(2)

        print("\n--- Etapa 1: Preenchendo campos com PyAutoGUI e 'Tab' ---")
        preencher_nome(dados_cliente.get('nome'))
        PAUSA_NAVEGACAO = 0.5
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        preencher_telefone(dados_cliente.get('telefone'))
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        preencher_item(dados_cliente.get('item'))
        pyautogui.press('tab', presses=3, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        preencher_vencimento(dados_cliente.get('vigencia'))
        pyautogui.press('tab', presses=5, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        selecionar_sair_em_renovacoes()
        pyautogui.press('tab', presses=1, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        
        preencher_observacoes(dados_cliente.get('observacao'))
        
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        selecionar_criar_tarefa()
        print("--- Etapa 1 concluída com sucesso! ---")

        esperar_agger_ficar_ocioso()

        print("\n--- Etapa 2: Selecionando Responsável com Pywinauto ---")
        if not selecionar_responsavel(dados_cliente.get('situacao')): return False
        print("--- Etapa 2 concluída com sucesso! ---")
        
        esperar_agger_ficar_ocioso()
        
        print("\n--- Etapa 3: Selecionando Vendedor com Pywinauto ---")
        if not selecionar_vendedor(dados_cliente.get('situacao')): return False
        print("--- Etapa 3 concluída com sucesso! ---")

        esperar_agger_ficar_ocioso()

        print("\n--- Etapa 4: Selecionando Status com Pywinauto ---")
        if not selecionar_status(dados_cliente): return False
        print("--- Etapa 4 concluída com sucesso! ---")

        esperar_agger_ficar_ocioso()

        print("\n--- Etapa 5: Anexando a(s) proposta(s) ---")
        lista_de_caminhos_completos = dados_cliente.get("anexos", [])
        if not lista_de_caminhos_completos:
            print("⚠️  Nenhum anexo encontrado no banco de dados para este cliente. Pulando etapa de anexo.")
        else:
            nomes_dos_arquivos_para_anexar = [os.path.basename(caminho) for caminho in lista_de_caminhos_completos]
            if not anexar_arquivos(nomes_dos_arquivos_para_anexar):
                print("🚨 Falha na etapa de anexo de arquivos.")
                return False
        print("--- Etapa 5 concluída com sucesso! ---")

        esperar_agger_ficar_ocioso()

        print("\n--- Etapa 6: Salvando a prospecção ---")
        if not salvar_prospeccao():
            print("🚨 Falha na etapa de salvamento.")
            return False
        print("--- Etapa 6 concluída com sucesso! ---")

        print("\n🎉🎉🎉 Processo completo finalizado com sucesso! 🎉🎉🎉")
        return True
    except Exception as e:
        print(f"🚨 ERRO: Falha durante a automação final.")
        print(f"   Detalhe do erro: {e}")
        return False