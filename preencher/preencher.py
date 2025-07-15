# seu_projeto/preencher/preencher.py (VERSÃO CORRIGIDA)
import pyautogui
import time

# Adicionamos 'status' à lista de importação
from . import (
    nome, telefone, item, vencimento, sair_em_renovacoes, 
    observacoes, criar_tarefa, responsavel, vendedor, status
)

def executar_preenchimento(dados_cliente: dict) -> bool:
    """
    Orquestra o preenchimento completo do formulário no sistema Agger.
    """
    try:
        print("Iniciando o preenchimento final com a sequência mapeada...")
        time.sleep(2)

        # --- ETAPA 1: PREENCHIMENTO COM PYAUTOGUI ---
        print("\n--- Etapa 1: Preenchendo campos com PyAutoGUI e 'Tab' ---")
        
        # A lógica de navegação com 'Tab' continua aqui...
        nome.preencher(dados_cliente.get('nome'))
        PAUSA_NAVEGACAO = 0.5
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        telefone.preencher(dados_cliente.get('telefone'))
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        item.preencher(dados_cliente.get('item'))
        pyautogui.press('tab', presses=3, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        vencimento.preencher(dados_cliente.get('vigencia'))
        pyautogui.press('tab', presses=5, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        sair_em_renovacoes.selecionar()
        pyautogui.press('tab', presses=1, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        observacoes.preencher(dados_cliente.get('observacao'))
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO); time.sleep(PAUSA_NAVEGACAO)
        criar_tarefa.selecionar()
        print("--- Etapa 1 concluída com sucesso! ---")

        # --- ETAPA 2: SELEÇÃO DE RESPONSÁVEL ---
        print("\n--- Etapa 2: Selecionando Responsável com Pywinauto ---")
        # CORREÇÃO: Passando apenas o valor da 'situacao' para a função
        if not responsavel.selecionar_responsavel(dados_cliente.get('situacao')):
            print("🚨 Falha na etapa de seleção do responsável.")
            return False
        print("--- Etapa 2 concluída com sucesso! ---")
        
        # --- ETAPA 3: SELEÇÃO DE VENDEDOR ---
        print("\n--- Etapa 3: Selecionando Vendedor com Pywinauto ---")
        # CORREÇÃO: Passando apenas o valor da 'situacao' para a função
        if not vendedor.selecionar(dados_cliente.get('situacao')):
            print("🚨 Falha na etapa de seleção do vendedor.")
            return False
        print("--- Etapa 3 concluída com sucesso! ---")

        # --- ETAPA 4: SELEÇÃO DE STATUS ---
        print("\n--- Etapa 4: Selecionando Status com Pywinauto ---")
        # Esta chamada está correta, pois o módulo 'status' foi feito para receber o dict inteiro
        if not status.selecionar(dados_cliente):
            print("🚨 Falha na etapa de seleção do status.")
            return False
        print("--- Etapa 4 concluída com sucesso! ---")

        print("\n🎉🎉🎉 Preenchimento completo do formulário finalizado com sucesso! 🎉🎉🎉")
        return True

    except Exception as e:
        print(f"🚨 ERRO: Falha durante a automação final.")
        print(f"   Detalhe do erro: {e}")
        return False
