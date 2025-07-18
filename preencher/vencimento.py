# Arquivo: preencher/vencimento.py (VERSÃO FINAL - MÉTODO DIRETO)

import pyautogui
import time
from datetime import date

def preencher(data_vencimento):
    """
    Preenche o campo de vencimento de forma direta e segura,
    sempre digitando a data completa.
    """
    
    data_final = None
    # PASSO 1: Determinar qual data usar
    if isinstance(data_vencimento, date):
        data_final = data_vencimento
        print(f"Usando data de vencimento do banco: {data_final.strftime('%d/%m/%Y')}")
    else:
        data_final = date.today()
        print(f"Data do banco não fornecida. Usando data de hoje: {data_final.strftime('%d/%m/%Y')}")

    # Formata a data para DDMMYYYY para digitação
    texto_data_digitar = data_final.strftime('%d%m%Y')
    
    print(f"Tentando preencher Vencimento digitando: '{texto_data_digitar}'...")
    try:
        # PASSO 2: Limpar completamente o campo antes de inserir.
        print("...Limpando o campo de data...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.press('delete')
        time.sleep(0.3)

        # PASSO 3: Digitar a data lentamente, que é o método mais seguro.
        pyautogui.write(texto_data_digitar, interval=0.1)
        
        print("✅ Vencimento preenchido via 'digitar'.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo de vencimento: {e}")
