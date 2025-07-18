# Arquivo: preencher/vencimento.py (VERSÃO ULTRA-ROBUSTA)

import pyautogui
import pyperclip
import time
from datetime import date

def preencher(data_vencimento):
    """
    Preenche o campo de vencimento de forma robusta:
    - Se uma data específica é fornecida, limpa o campo e tenta colar/digitar.
    - Se não, usa o atalho do Agger (digitar '1' e Enter) para a data de hoje.
    """
    
    # CENÁRIO 1: Temos uma data específica vinda do banco de dados.
    if isinstance(data_vencimento, date):
        data_final = data_vencimento
        print(f"Usando data de vencimento do banco: {data_final.strftime('%d/%m/%Y')}")
        
        # Prepara a data em dois formatos: um para colar, outro para digitar.
        texto_data_colar = data_final.strftime('%d/%m/%Y')
        texto_data_digitar = data_final.strftime('%d%m%Y')
        
        print(f"Tentando preencher Vencimento: '{texto_data_colar}'...")
        try:
            # PASSO 1: Limpar completamente o campo antes de inserir.
            print("...Limpando o campo de data...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)

            # PASSO 2: Tentar o método de colar, que é mais confiável.
            print(f"...Tentando colar a data no formato {texto_data_colar}...")
            pyperclip.copy(texto_data_colar)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            print("✅ Vencimento específico preenchido via 'colar'.")

        except Exception as e:
            # PASSO 3: Se colar falhar, usar o método de digitar como plano B.
            print(f"🚨 Colar falhou: {e}. Tentando digitar como plano B...")
            pyautogui.write(texto_data_digitar, interval=0.1)
            print("✅ Vencimento específico preenchido via 'digitar'.")

    # CENÁRIO 2: Nenhuma data do banco. Usaremos o atalho do Agger.
    else:
        print("Data do banco não fornecida. Usando o atalho do Agger para a data de hoje...")
        try:
            # --- MUDANÇA: Voltando a usar o atalho '1' + 'Enter', que é o mais confiável ---
            print("Digitando o atalho '1' para a data de hoje...")
            pyautogui.write('1', interval=0.1)

            # Pausa para a aplicação processar o atalho
            print("... Pausa de 1 segundo após digitar o atalho ...")
            time.sleep(1)
            
            # Pressiona a tecla Enter para confirmar
            pyautogui.press('enter')
            
            print("✅ Vencimento preenchido com a data de hoje usando o atalho '1' + 'Enter'.")
        except Exception as e:
            print(f"🚨 ERRO ao tentar usar o atalho para data de hoje: {e}")
