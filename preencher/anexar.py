# Arquivo: preencher/anexar.py (VERSÃO FINAL CORRIGIDA: FOCO DIRETO COM ALT+N E LIMPEZA)

import time
import os
import pyautogui
import pyperclip
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError
from config import CAMINHO_LOCAL_PROPOSTAS

APP_TITLE = "AGGER GESTOR"

def anexar(lista_nomes_arquivos: list[str]) -> bool:
    """
    Automatiza o processo de anexar múltiplos arquivos sequencialmente.
    """
    if not lista_nomes_arquivos:
        print("⚠️ AVISO: Nenhuma lista de arquivos fornecida para anexar.")
        return True

    print(f"\n--- INICIANDO ANEXO DE {len(lista_nomes_arquivos)} ARQUIVO(S) ---")
    
    sucessos = 0
    falhas = 0

    for nome_arquivo in lista_nomes_arquivos:
        print(f"\n[INFO] Anexando arquivo: '{nome_arquivo}'...")
        caminho_completo = os.path.join(CAMINHO_LOCAL_PROPOSTAS, nome_arquivo)
        
        if not os.path.exists(caminho_completo):
            print(f"🚨 ERRO: O arquivo para anexar não foi encontrado em: {caminho_completo}")
            falhas += 1
            continue

        try:
            print("[INFO] Conectando ao app AGGER GESTOR...")
            app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
            dlg = app.window(title=APP_TITLE)
            dlg.set_focus()
            
            print("[ACAO] Procurando e clicando em 'INCLUIR ANEXOS'...")
            anexar_button = dlg.child_window(title="INCLUIR ANEXOS", control_type="MenuItem")
            anexar_button.wait('visible enabled', timeout=15)
            anexar_button.click_input()
            print("[SUCESSO] Clique em 'INCLUIR ANEXOS' realizado.")

            # --- PASSO 1: COLAR O CAMINHO DA PASTA (Foco Robusto) ---
            print("[INFO] Aguardando 4 segundos para a janela de seleção de arquivo aparecer...")
            time.sleep(4) 

            print(f"[ACAO] Navegando para a pasta: {CAMINHO_LOCAL_PROPOSTAS}")
            pyperclip.copy(CAMINHO_LOCAL_PROPOSTAS)

            # Foca na barra de endereço (Ctrl+L) e cola o caminho
            pyautogui.hotkey('ctrl', 'l'); time.sleep(0.3) 
            pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5)
            
            # Pressiona Enter para abrir o diretório
            pyautogui.press('enter'); time.sleep(1.0) 

            # --- PASSO 2: Focar no campo "Nome:" usando Alt+N ---
            print(f"[ACAO] Focando no campo 'Nome:' usando Alt+N para bypassar a Pesquisa...")
            
            # O ESC tira o foco do campo Pesquisar (vermelho) e o Alt+N força o foco no campo Nome (azul).
            pyautogui.press('esc'); time.sleep(0.5)
            pyautogui.hotkey('alt', 'n'); time.sleep(0.5) 
            
            # --- PASSO 3: Colar o nome do arquivo e confirmar (CORRIGIDO) ---
            print(f"[ACAO] Colando o nome do arquivo: {nome_arquivo}")
            pyperclip.copy(nome_arquivo) 
            
            # ADICIONADO: Forçar a limpeza do campo antes de colar
            pyautogui.hotkey('ctrl', 'a'); time.sleep(0.1) # Seleciona todo o texto
            pyautogui.press('delete'); time.sleep(0.1)     # Apaga o texto
            
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)

            print("[ACAO] Pressionando 'Enter' para confirmar o anexo...")
            pyautogui.press('enter')
            
            print("[INFO] Aguardando 4 segundos para o anexo ser processado...")
            time.sleep(4)

            print(f"✅ Anexo do arquivo '{nome_arquivo}' realizado com sucesso!")
            sucessos += 1

        except (ElementNotFoundError, TimeoutError) as e:
            print(f"🚨 ERRO: Não foi possível encontrar o app ou um de seus elementos ao tentar anexar '{nome_arquivo}': {e}")
            falhas += 1
            break 
        except Exception as e:
            print(f"🚨 ERRO INESPERADO durante o anexo de '{nome_arquivo}': {e}")
            falhas += 1
            continue

    print("\n--- RESUMO DO PROCESSO DE ANEXO ---")
    print(f"✅ Sucessos: {sucessos}")
    print(f"🚨 Falhas: {falhas}")
    
    return falhas == 0