# seu_projeto/preencher/preencher.py (VERSÃO FINAL COM SALVAR)
import pyautogui
import time

# Importa cada função diretamente de seu módulo
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
from .anexar import anexar as anexar_arquivo
# --- NOVA IMPORTAÇÃO ---
from .salvar import salvar_prospeccao

def executar_preenchimento(dados_cliente: dict, nome_arquivo_pdf: str) -> bool:
    """
    Orquestra o preenchimento, anexo e salvamento da prospecção.
    """
    try:
        print("Iniciando o preenchimento final com a sequência mapeada...")
        time.sleep(2)

        # --- ETAPA 1: PREENCHIMENTO COM PYAUTOGUI ---
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
        preencher_observacoes(dados_cliente)
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        selecionar_criar_tarefa()
        print("--- Etapa 1 concluída com sucesso! ---")

        # --- ETAPA 2: SELEÇÃO DE RESPONSÁVEL ---
        print("\n--- Etapa 2: Selecionando Responsável com Pywinauto ---")
        if not selecionar_responsavel(dados_cliente.get('situacao')): return False
        print("--- Etapa 2 concluída com sucesso! ---")
        
        # --- ETAPA 3: SELEÇÃO DE VENDEDOR ---
        print("\n--- Etapa 3: Selecionando Vendedor com Pywinauto ---")
        if not selecionar_vendedor(dados_cliente.get('situacao')): return False
        print("--- Etapa 3 concluída com sucesso! ---")

        # --- ETAPA 4: SELEÇÃO DE STATUS ---
        print("\n--- Etapa 4: Selecionando Status com Pywinauto ---")
        if not selecionar_status(dados_cliente): return False
        print("--- Etapa 4 concluída com sucesso! ---")

        # --- ETAPA 5: ANEXAR O PDF ---
        print("\n--- Etapa 5: Anexando a proposta em PDF ---")
        if not anexar_arquivo(nome_arquivo_pdf): return False
        print("--- Etapa 5 concluída com sucesso! ---")

        # --- NOVA ETAPA 6: SALVAR A PROSPECÇÃO ---
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
