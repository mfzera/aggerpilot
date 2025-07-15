# seu_projeto/preencher/preencher.py (VERSÃO MAIS PACIENTE)
import pyautogui
import time

from . import (
    nome, telefone, item, vencimento, sair_em_renovacoes, 
    observacoes, criar_tarefa
)

def executar_preenchimento(dados_cliente: dict) -> bool:
    try:
        print("Iniciando o preenchimento final com a sequência mapeada...")
        time.sleep(2)

        # Posição 0: Ancora no campo 'Nome'
        nome.preencher(dados_cliente.get('nome'))
        
        # Pausa maior para garantir a navegação
        PAUSA_NAVEGACAO = 0.5 

        print("Navegando para o campo 'Telefone' (Posição 4)...")
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO) # Pausa extra antes de digitar
        telefone.preencher(dados_cliente.get('telefone'))

        print("Navegando para o campo 'Item' (Posição 8)...")
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO)
        item.preencher(dados_cliente.get('item'))

        print("Navegando para o campo 'Vencimento' (Posição 11)...")
        pyautogui.press('tab', presses=3, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO)
        vencimento.preencher(dados_cliente.get('vigencia'))
        
        print("Navegando para 'Sair em renovações' (Posição 16)...")
        pyautogui.press('tab', presses=5, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO)
        sair_em_renovacoes.selecionar()

        print("Navegando para 'Observações' (Posição 17)...")
        pyautogui.press('tab', presses=1, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO)
        observacoes.preencher(dados_cliente.get('observacao'))
        
        print("Navegando para 'Criar tarefa' (Posição 21)...")
        pyautogui.press('tab', presses=4, interval=PAUSA_NAVEGACAO)
        time.sleep(PAUSA_NAVEGACAO)
        criar_tarefa.selecionar()

        print("🎉🎉🎉 Preenchimento completo do formulário finalizado com sucesso! 🎉🎉🎉")
        return True

    except Exception as e:
        print(f"🚨 ERRO: Falha durante a automação final com PyAutoGUI.")
        print(f"Detalhe do erro: {e}")
        return False