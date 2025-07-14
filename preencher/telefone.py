# seu_projeto/preencher/telefone.py

import pyautogui
import time

# Garanta que você tem o screenshot 'label_telefone1.png' na pasta 'imagens/'
IMAGEM_LABEL_TELEFONE = 'imagens/label_telefone1.png' 
OFFSET_X = 100 # O deslocamento para o telefone pode ser diferente, ajuste se precisar

def preencher(numero_telefone: str):
    """
    Encontra o RÓTULO do campo Telefone 1 e o preenche.
    """
    # A função do banco sempre retorna "0", então vamos garantir que o tipo é string
    # para a função write do pyautogui.
    texto_para_escrever = str(numero_telefone)

    try:
        print(f"Procurando pelo rótulo 'Telefone 1'...")
        
        local_label = pyautogui.locateOnScreen(IMAGEM_LABEL_TELEFONE, confidence=0.8)
        
        if local_label is None:
            raise Exception(f"Não foi possível encontrar o RÓTULO '{IMAGEM_LABEL_TELEFONE}' na tela.")

        ponto_central_label = pyautogui.center(local_label)
        
        print(f"Rótulo encontrado! Clicando ao lado para inserir '{texto_para_escrever}'...")
        pyautogui.click(ponto_central_label.x + OFFSET_X, ponto_central_label.y)
        
        time.sleep(0.5)

        pyautogui.write(texto_para_escrever, interval=0.05)

        print("✅ Campo 'Telefone 1' preenchido.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo 'Telefone 1'.")
        raise e