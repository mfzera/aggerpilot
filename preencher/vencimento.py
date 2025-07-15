# seu_projeto/preencher/vencimento.py
import pyautogui
from datetime import date # Importa a classe 'date' da biblioteca 'datetime'

def preencher(data_vencimento):
    """
    Preenche o campo de vencimento. Usa a data de hoje se nenhuma for fornecida.
    """
    
    # Verifica se recebemos uma data válida do banco de dados
    if isinstance(data_vencimento, date):
        data_final = data_vencimento
        print(f"Usando data de vencimento do banco: {data_final.strftime('%d/%m/%Y')}")
    else:
        # Se não, pega a data de hoje como padrão
        data_final = date.today()
        print(f"Data do banco não fornecida. Usando data de hoje: {data_final.strftime('%d/%m/%Y')}")

    # Formata a data para DDMMYYYY, sem as barras, para digitação.
    texto_data = data_final.strftime('%d%m%Y')
    
    print(f"Digitando Vencimento: '{texto_data}'...")
    pyautogui.write(texto_data, interval=0.05)
    print("✅ Vencimento preenchido.")