# seu_projeto/preencher/observacoes.py

import pyautogui
import time

# Garanta que você terá um screenshot 'label_observacao.png'
IMAGEM_LABEL_OBSERVACAO = 'imagens/label_observacoes.png'
OFFSET_X = 150 # Ajuste conforme necessário

def preencher(texto_da_observacao: str):
    if not texto_da_observacao:
        print("AVISO: Texto de observação não fornecido. Pulando.")
        return
        
    try:
        print(f"Procurando pelo rótulo 'Observação'...")
        
        local_label = pyautogui.locateOnScreen(IMAGEM_LABEL_OBSERVACAO, confidence=0.8)
        
        if local_label is None:
            raise Exception(f"Não foi possível encontrar o RÓTULO '{IMAGEM_LABEL_OBSERVACAO}' na tela.")

        ponto_central_label = pyautogui.center(local_label)
        
        print(f"Rótulo encontrado! Clicando ao lado para inserir a observação...")
        pyautogui.click(ponto_central_label.x + OFFSET_X, ponto_central_label.y)
        
        time.sleep(0.5)
        pyautogui.write(texto_da_observacao, interval=0.02)
        print("✅ Campo 'Observação' preenchido.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo 'Observação'.")
        raise e