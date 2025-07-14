# seu_projeto/preencher/nome.py (VERSÃO FINAL COM A LÓGICA EMBUTIDA)

import pyautogui
import time

IMAGEM_LABEL_NOME = 'imagens/label_nome.png' 
OFFSET_X = 150 

def preencher(nome_do_cliente: str):
    """
    Encontra o RÓTULO do campo e clica ao lado dele para preencher.
    Também adiciona um sufixo ao nome antes de preencher.
    """
    if not nome_do_cliente:
        print("AVISO: Nome do cliente não fornecido. Pulando.")
        return

    # ==========================================================
    # --- LÓGICA DE MODIFICAÇÃO MOVIDA PARA CÁ ---
    # Nota: No seu pedido você usou aspa simples (') e acento grave (`).
    # Vou usar a aspa simples. Se quiser o outro, é só trocar.
    nome_modificado = nome_do_cliente + " '"
    print(f"ℹ️  Nome original: '{nome_do_cliente}' -> Modificado para: '{nome_modificado}'")
    # --- FIM DA LÓGICA DE MODIFICAÇÃO ---
    # ==========================================================

    try:
        print(f"Procurando pelo rótulo do campo 'Nome'...")
        
        local_label = pyautogui.locateOnScreen(IMAGEM_LABEL_NOME, confidence=0.8)
        
        if local_label is None:
            raise Exception(f"Não foi possível encontrar o RÓTULO '{IMAGEM_LABEL_NOME}' na tela.")

        ponto_central_label = pyautogui.center(local_label)
        
        print(f"Rótulo encontrado! Clicando ao lado para inserir o nome modificado...")
        pyautogui.click(ponto_central_label.x + OFFSET_X, ponto_central_label.y)
        
        time.sleep(0.5)

        # Usamos a variável com o nome já modificado
        pyautogui.write(nome_modificado, interval=0.05)

        print("✅ Campo 'nome' preenchido corretamente.")

    except Exception as e:
        print(f"🚨 ERRO ao tentar preencher o campo 'nome'.")
        raise e