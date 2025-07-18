# Arquivo: preencher/nome.py (VERSÃO HÍBRIDA - ROBUSTA E BASEADA NO SEU CÓDIGO)

import pyautogui
import pyperclip
import time

IMAGEM_LABEL_NOME = 'imagens/label_nome.png' 
OFFSET_X = 150 

def preencher(nome_do_cliente: str):
    """
    Encontra o RÓTULO do campo e clica ao lado dele para preencher.
    Agora espera o rótulo aparecer e usa copiar/colar para mais confiabilidade.
    """
    if not nome_do_cliente:
        print("AVISO: Nome do cliente não fornecido. Pulando.")
        return

    # Mantém a sua lógica original de modificação do nome
    nome_modificado = nome_do_cliente + " ''"
    print(f"ℹ️  Nome original: '{nome_do_cliente}' -> Modificado para: '{nome_modificado}'")

    try:
        print(f"Procurando pelo rótulo do campo 'Nome' (aguardando até 10 segundos)...")
        
        # --- MELHORIA: Lógica de espera pela imagem ---
        local_label = None
        start_time = time.time()
        while time.time() - start_time < 10:
            # Tenta encontrar a imagem na tela
            local_label = pyautogui.locateOnScreen(IMAGEM_LABEL_NOME, confidence=0.8)
            if local_label:
                break # Se encontrou, sai do loop
            time.sleep(0.5) # Se não, espera um pouco e tenta de novo

        if local_label is None:
            # Se não encontrou após 10 segundos, lança o erro.
            raise Exception(f"Não foi possível encontrar o RÓTULO '{IMAGEM_LABEL_NOME}' na tela.")

        # --- Lógica de clique original (mantida) ---
        ponto_central_label = pyautogui.center(local_label)
        print(f"Rótulo encontrado! Clicando ao lado para inserir o nome modificado...")
        pyautogui.click(ponto_central_label.x + OFFSET_X, ponto_central_label.y)
        time.sleep(0.5)

        # --- MELHORIA: Lógica de preenchimento (copiar/colar) ---
        pyperclip.copy(nome_modificado)
        pyautogui.hotkey('ctrl', 'v')

        print("✅ Campo 'nome' preenchido corretamente.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo 'nome'.")
        # Re-lança a exceção para que a função principal (preencher_todos) saiba que falhou.
        raise e
