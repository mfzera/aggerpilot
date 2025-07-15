# seu_projeto/preencher/item.py (VERSÃO COM VALOR PADRÃO "0")
import pyautogui

def preencher(texto_do_item: str):
    """
    Preenche o campo Item. Se o valor do banco for vazio, usa "0" como padrão.
    """
    
    # Se o valor do banco for nulo ou vazio...
    if not texto_do_item:
        print('AVISO: Texto do item não fornecido pelo banco. Usando valor padrão "0".')
        # ...definimos "0" como o texto a ser escrito.
        texto_para_escrever = "0"
    else:
        # Senão, usamos o valor que veio do banco.
        texto_para_escrever = texto_do_item

    # O resto da função continua igual, mas usando a variável 'texto_para_escrever'
    try:
        print(f"Digitando Item: '{texto_para_escrever}'...")
        pyautogui.write(texto_para_escrever, interval=0.05)
        print("✅ Item preenchido.")
    except Exception as e:
        # Adicionado um 'try/except' para o caso de falha na digitação
        print(f"🚨 ERRO ao tentar preencher o campo 'Item'.")
        raise e