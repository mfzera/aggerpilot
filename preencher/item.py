# seu_projeto/preencher/item.py

import pyautogui
import time

# Garanta que você tem o screenshot 'label_item.png' na pasta 'imagens/'
IMAGEM_LABEL_ITEM = 'imagens/label_item.png'
# O campo item parece ser maior, talvez precise de um offset diferente.
OFFSET_X = 150 

def preencher(texto_do_item: str):
    """
    Encontra o RÓTULO do campo Item e o preenche.
    """
    if not texto_do_item:
        print("AVISO: Texto do item não fornecido. Pulando.")
        return
        
    try:
        print(f"Procurando pelo rótulo 'Item'...")
        
        local_label = pyautogui.locateOnScreen(IMAGEM_LABEL_ITEM, confidence=0.8)
        
        if local_label is None:
            raise Exception(f"Não foi possível encontrar o RÓTULO '{IMAGEM_LABEL_ITEM}' na tela.")

        ponto_central_label = pyautogui.center(local_label)
        
        print(f"Rótulo encontrado! Clicando ao lado para inserir '{texto_do_item}'...")
        pyautogui.click(ponto_central_label.x + OFFSET_X, ponto_central_label.y)
        
        time.sleep(0.5)

        pyautogui.write(texto_do_item, interval=0.05)

        print("✅ Campo 'Item' preenchido.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo 'Item'.")
        raise e