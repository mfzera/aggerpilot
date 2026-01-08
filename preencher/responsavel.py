# Arquivo: preencher/responsavel.py (VERSÃO CORRIGIDA COM SELEÇÃO VIA TECLADO)

import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

APP_TITLE = "AGGER GESTOR"

def selecionar_responsavel(situacao: str) -> bool:
    """
    Conecta-se ao aplicativo AGGER GESTOR para selecionar o responsável,
    usando digitação por teclado para maior robustez.
    """
    try:
        print(f"[INFO] Módulo Responsável: Conectando ao app '{APP_TITLE}'...")
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)

        dlg.set_focus()
        dlg.wait("ready", timeout=10)
        
        print("[INFO] Módulo Responsável: Janela principal focada.")

        # --- PASSO 1: Clicar no ComboBox "Responsável" ---
        print("[ACAO] Procurando e clicando no ComboBox de 'Responsável'...")
        try:
            responsavel_combo = dlg.child_window(control_type="ComboBox", found_index=6)

            if responsavel_combo.exists():
                responsavel_combo.click_input()
                print("[SUCESSO] Clique no ComboBox de 'Responsável' realizado.")
            else:
                print("[ERRO] Não foi possível encontrar o ComboBox de 'Responsável' pelo índice.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar clicar no ComboBox de 'Responsável': {e}")
            return False

        # --- PASSO 2: Aguardar as opções do ComboBox aparecerem ---
        print("\n[INFO] Aguardando 1.5 segundos para a lista abrir...")
        time.sleep(1.5)

        # --- PASSO 3: Selecionar o responsável via teclado (MÉTODO ROBUSTO) ---
        responsavel_nome = "GESTAO"

        print(f"[ACAO] Selecionando '{responsavel_nome}' via teclado...")
        try:
            # O método 'type_keys' é mais confiável pois envia os comandos para a janela específica.
            # Digita o nome completo para selecionar na lista.
            dlg.type_keys(responsavel_nome, with_spaces=True)
            time.sleep(1) # Pausa para a interface reagir à digitação

            # Pressiona Enter para confirmar a seleção
            dlg.type_keys('{ENTER}')
            time.sleep(1) # Pausa para a seleção ser processada e a lista fechar

            print(f"[SUCESSO] Responsável '{responsavel_nome}' selecionado via teclado.")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao tentar selecionar o responsável via teclado: {e}")
            return False

    except ElementNotFoundError:
        print(f"[ERRO FATAL] O aplicativo '{APP_TITLE}' não foi encontrado. Ele está aberto?")
        return False
    except Exception as e:
        print(f"[ERRO INESPERADO] Ocorreu uma falha no módulo responsável: {e}")
        return False

