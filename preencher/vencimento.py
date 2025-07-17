# Arquivo: preencher/vencimento.py (VERSÃO MELHORADA COM COPIAR/COLAR)

import pyautogui
import pyperclip  # Importa a biblioteca para a área de transferência
import time
from datetime import date

def preencher(data_vencimento):
    """
    Preenche o campo de vencimento. Usa a data de hoje se nenhuma for fornecida.
    Agora usa o método de copiar/colar para maior confiabilidade.
    """
    
    # Verifica se recebemos uma data válida do banco de dados
    if isinstance(data_vencimento, date):
        data_final = data_vencimento
        print(f"Usando data de vencimento do banco: {data_final.strftime('%d/%m/%Y')}")
    else:
        # Se não, pega a data de hoje como padrão
        data_final = date.today()
        print(f"Data do banco não fornecida. Usando data de hoje: {data_final.strftime('%d/%m/%Y')}")

    # Formata a data para DDMMYYYY, sem as barras
    texto_data = data_final.strftime('%d%m%Y')
    
    print(f"Colando Vencimento: '{texto_data}'...")
    try:
        # PASSO 1: Copia o texto da data para a área de transferência
        pyperclip.copy(texto_data)
        time.sleep(0.3)  # Pequena pausa para garantir que o sistema operacional atualizou a área de transferência

        # PASSO 2: Usa o atalho Ctrl+V para colar o texto no campo
        pyautogui.hotkey('ctrl', 'v')
        
        print("✅ Vencimento preenchido via 'colar'.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar colar a data: {e}")
        print("...Tentando digitar como plano B (mais devagar)...")
        # Como plano B, digita o texto mais lentamente, como você sugeriu.
        pyautogui.write(texto_data, interval=0.1)
        print("✅ Vencimento preenchido via 'digitar'.")
