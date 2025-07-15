import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

APP_TITLE = "AGGER GESTOR"

def selecionar(dados_cliente: dict) -> bool:
    """
    Conecta-se ao aplicativo AGGER GESTOR para selecionar o Status da prospecção.

    Args:
        dados_cliente (dict): Dicionário contendo os dados do cliente.
                              Espera-se as chaves 'situacao' e 'perdido'.

    Returns:
        bool: True se o status foi selecionado com sucesso, False caso contrário.
    """
    try:
        print(f"[INFO] Módulo Status: Conectando ao app '{APP_TITLE}'...")
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)

        dlg.set_focus()
        dlg.wait("ready", timeout=10)
        
        print("[INFO] Módulo Status: Janela principal focada.")

        # --- PASSO 1: Determinar qual status selecionar ---
        situacao = dados_cliente.get('situacao', '').lower()
        perdido = dados_cliente.get('perdido', '').lower() # Supondo que 'perdido' virá dos dados

        status_nome = ""
        if situacao == "cancelado" or perdido == "perdido":
            status_nome = "PERDIDO"
        else:
            status_nome = "GANHO"
        
        print(f"[INFO] Condição: situacao='{situacao}', perdido='{perdido}'. Status a ser selecionado: '{status_nome}'")

        # --- PASSO 2: Clicar no ComboBox "Status" ---
        print("[ACAO] Procurando e clicando no ComboBox de 'Status'...")
        try:
            # ATENÇÃO: O índice 4 foi baseado no seu script.
            # Verifique se esta é a posição correta do ComboBox 'Status'.
            status_combo = dlg.child_window(control_type="ComboBox", found_index=4)

            if status_combo.exists():
                status_combo.click_input()
                print("[SUCESSO] Clique no ComboBox de 'Status' realizado.")
            else:
                print("[ERRO] Não foi possível encontrar o ComboBox de 'Status' pelo índice.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar clicar no ComboBox de 'Status': {e}")
            return False

        # --- PASSO 3: Aguardar e selecionar a opção ---
        print("\n[INFO] Aguardando 2 segundos para as opções aparecerem...")
        time.sleep(2)

        print(f"[ACAO] Procurando e selecionando o status: '{status_nome}'...")
        try:
            app_top = app.top_window()
            item_text = app_top.child_window(title=status_nome, control_type="Text", found_index=0)

            if item_text.exists():
                item_a_selecionar = item_text.parent()
                item_a_selecionar.set_focus()
                item_a_selecionar.click_input()
                print(f"[SUCESSO] Status '{status_nome}' selecionado.")
                return True
            else:
                print(f"[ERRO] Não foi possível encontrar o texto do status '{status_nome}' na lista.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar selecionar o status: {e}")
            return False

    except ElementNotFoundError:
        print(f"[ERRO FATAL] O aplicativo '{APP_TITLE}' não foi encontrado. Ele está aberto?")
        return False
    except Exception as e:
        print(f"[ERRO INESPERADO] Ocorreu uma falha no módulo status: {e}")
        return False
