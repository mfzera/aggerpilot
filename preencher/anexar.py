import time
import os
import pyautogui
import pyperclip
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError

APP_TITLE = "AGGER GESTOR"
DIALOG_TITLE = "Abrir" # Título da janela de seleção de arquivo
# A constante agora é global e pode ser importada por outros módulos.
PASTA_PROPOSTAS_LOCAL = r"C:\Users\migue\Desktop\automação\propostas_vps"

def anexar(nome_arquivo_pdf: str) -> bool:
    """
    Automatiza o processo de anexar um arquivo PDF na tela de prospecção.
    A função agora recebe apenas o nome do arquivo e o combina com a pasta local fixa.

    Args:
        nome_arquivo_pdf (str): O nome do arquivo (ex: "MIGUEL FERREIRA.pdf").

    Returns:
        bool: True se o anexo foi realizado com sucesso, False caso contrário.
    """
    print("\n--- INICIANDO ANEXO DE PROPOSTA ---")
    
    caminho_completo_pdf = os.path.join(PASTA_PROPOSTAS_LOCAL, nome_arquivo_pdf)
    
    if not os.path.exists(caminho_completo_pdf):
        print(f"🚨 ERRO: O arquivo para anexar não foi encontrado em: {caminho_completo_pdf}")
        return False

    try:
        # 1. Conectar-se à aplicação e clicar no botão de anexo
        print("[INFO] Conectando ao app AGGER GESTOR...")
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)
        dlg.set_focus()
        
        print("[ACAO] Procurando e clicando em 'INCLUIR ANEXOS'...")
        anexar_button = dlg.child_window(title="INCLUIR ANEXOS", control_type="MenuItem")
        anexar_button.wait('visible enabled', timeout=15)
        anexar_button.click_input()
        print("[SUCESSO] Clique em 'INCLUIR ANEXOS' realizado.")

        # 2. Manipular a janela de seleção de arquivo com pyautogui
        print("[INFO] Aguardando 2 segundos para a janela de seleção de arquivo aparecer...")
        time.sleep(2)

        print(f"[ACAO] Copiando o caminho da pasta para o clipboard: {PASTA_PROPOSTAS_LOCAL}")
        pyperclip.copy(PASTA_PROPOSTAS_LOCAL)
        
        pyautogui.hotkey('ctrl', 'l'); time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v'); time.sleep(1)
        pyautogui.press('enter'); time.sleep(1)

        print(f"[ACAO] Digitando o nome do arquivo: {nome_arquivo_pdf}")
        pyautogui.hotkey('alt', 'n'); time.sleep(0.5)
        pyautogui.write(nome_arquivo_pdf, interval=0.05)
        time.sleep(1)

        # --- CORREÇÃO AQUI ---
        # 3. Pressionar 'Enter' para confirmar a seleção do arquivo.
        # Esta abordagem é mais direta e menos propensa a erros de foco
        # do que tentar reconectar com pywinauto.
        print("[ACAO] Pressionando 'Enter' para confirmar o anexo...")
        pyautogui.press('enter')
        
        # Adiciona uma pausa para o diálogo fechar e o anexo ser processado.
        print("[INFO] Aguardando 3 segundos para o anexo ser processado...")
        time.sleep(3)

        print("✅ Anexo realizado com sucesso!")
        return True

    except (ElementNotFoundError, TimeoutError) as e:
        print(f"🚨 ERRO: Não foi possível encontrar o app ou um de seus elementos: {e}")
        return False
    except Exception as e:
        print(f"🚨 ERRO INESPERADO durante o processo de anexo: {e}")
        return False
