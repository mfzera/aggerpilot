import time
import os
import pyautogui
import pyperclip
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError

APP_TITLE = "AGGER GESTOR"
PASTA_PROPOSTAS_LOCAL = r"C:\Users\migue\Desktop\automação\propostas_vps"

def anexar(lista_nomes_arquivos_pdf: list[str]) -> bool:
    """
    Automatiza o processo de anexar múltiplos arquivos PDF sequencialmente.
    
    A função itera sobre uma lista de nomes de arquivos, anexando um por um.

    Args:
        lista_nomes_arquivos_pdf (list[str]): Uma lista com os nomes dos arquivos
                                              (ex: ["MIGUEL FERREIRA.pdf", "MIGUEL FERREIRA 2.pdf"]).

    Returns:
        bool: True se TODOS os anexos foram realizados com sucesso, False caso contrário.
    """
    if not lista_nomes_arquivos_pdf:
        print("⚠️ AVISO: Nenhuma lista de arquivos fornecida para anexar.")
        return True # Retorna True pois não havia nada a fazer, não é um erro.

    print(f"\n--- INICIANDO ANEXO DE {len(lista_nomes_arquivos_pdf)} PROPOSTA(S) ---")
    
    sucessos = 0
    falhas = 0

    # 1. MODIFICAÇÃO: Loop para processar cada arquivo da lista
    for nome_arquivo_pdf in lista_nomes_arquivos_pdf:
        print(f"\n[INFO] Anexando arquivo: '{nome_arquivo_pdf}'...")
        caminho_completo_pdf = os.path.join(PASTA_PROPOSTAS_LOCAL, nome_arquivo_pdf)
        
        if not os.path.exists(caminho_completo_pdf):
            print(f"🚨 ERRO: O arquivo para anexar não foi encontrado em: {caminho_completo_pdf}")
            falhas += 1
            continue # Pula para o próximo arquivo da lista

        try:
            # 2. A LÓGICA DE ANEXO AGORA ESTÁ DENTRO DO LOOP
            # Conectar-se à aplicação e clicar no botão de anexo
            print("[INFO] Conectando ao app AGGER GESTOR...")
            app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
            dlg = app.window(title=APP_TITLE)
            dlg.set_focus()
            
            print("[ACAO] Procurando e clicando em 'INCLUIR ANEXOS'...")
            anexar_button = dlg.child_window(title="INCLUIR ANEXOS", control_type="MenuItem")
            anexar_button.wait('visible enabled', timeout=15)
            # Usamos click_input() para cada anexo, pois é mais confiável
            anexar_button.click_input()
            print("[SUCESSO] Clique em 'INCLUIR ANEXOS' realizado.")

            # Manipular a janela de seleção de arquivo com pyautogui
            print("[INFO] Aguardando 2 segundos para a janela de seleção de arquivo aparecer...")
            time.sleep(2)

            print(f"[ACAO] Colando o caminho da pasta: {PASTA_PROPOSTAS_LOCAL}")
            pyperclip.copy(PASTA_PROPOSTAS_LOCAL)
            pyautogui.hotkey('ctrl', 'l'); time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v'); time.sleep(1)
            pyautogui.press('enter'); time.sleep(1)

            print(f"[ACAO] Digitando o nome do arquivo: {nome_arquivo_pdf}")
            pyautogui.hotkey('alt', 'n'); time.sleep(0.5)
            pyautogui.write(nome_arquivo_pdf, interval=0.05)
            time.sleep(1)

            print("[ACAO] Pressionando 'Enter' para confirmar o anexo...")
            pyautogui.press('enter')
            
            print("[INFO] Aguardando 3 segundos para o anexo ser processado...")
            time.sleep(3)

            print(f"✅ Anexo do arquivo '{nome_arquivo_pdf}' realizado com sucesso!")
            sucessos += 1

        except (ElementNotFoundError, TimeoutError) as e:
            print(f"🚨 ERRO: Não foi possível encontrar o app ou um de seus elementos ao tentar anexar '{nome_arquivo_pdf}': {e}")
            falhas += 1
            # Se a janela principal sumiu, talvez seja melhor parar tudo.
            # Se for só um erro de timeout no botão, o loop pode continuar.
            # Por segurança, vamos parar se o app não for encontrado.
            break 
        except Exception as e:
            print(f"🚨 ERRO INESPERADO durante o anexo de '{nome_arquivo_pdf}': {e}")
            falhas += 1
            continue

    # 3. MODIFICAÇÃO: Resumo final
    print("\n--- RESUMO DO PROCESSO DE ANEXO ---")
    print(f"✅ Sucessos: {sucessos}")
    print(f"🚨 Falhas: {falhas}")
    
    return falhas == 0 # Retorna True somente se não houver nenhuma falha