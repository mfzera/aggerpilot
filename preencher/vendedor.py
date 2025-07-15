import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

APP_TITLE = "AGGER GESTOR"

def selecionar(situacao: str) -> bool:
    """
    Conecta-se ao aplicativo AGGER GESTOR, que já deve estar aberto e focado
    na tela de prospecção, para selecionar o vendedor.

    Args:
        situacao (str): A situação do cadastro. Pode ser usada para determinar
                        qual vendedor será selecionado.

    Returns:
        bool: True se o vendedor foi selecionado com sucesso, False caso contrário.
    """
    try:
        print(f"[INFO] Módulo Vendedor: Conectando ao app '{APP_TITLE}'...")
        # Conecta-se à aplicação que já está em execução
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)

        # Garante que a janela está pronta para receber inputs
        dlg.set_focus()
        dlg.wait("ready", timeout=10)
        
        print("[INFO] Módulo Vendedor: Janela principal focada.")

        # --- PASSO 1: Clicar no ComboBox "Vendedor" ---
        print("[ACAO] Procurando e clicando no ComboBox de 'Vendedor'...")
        try:
            # ATENÇÃO: O índice 3 foi baseado no seu script.
            # Verifique se esta é a posição correta do ComboBox 'Vendedor'.
            vendedor_combo = dlg.child_window(control_type="ComboBox", found_index=3)

            if vendedor_combo.exists():
                vendedor_combo.click_input()
                print("[SUCESSO] Clique no ComboBox de 'Vendedor' realizado.")
            else:
                print("[ERRO] Não foi possível encontrar o ComboBox de 'Vendedor' pelo índice.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar clicar no ComboBox de 'Vendedor': {e}")
            return False

        # --- PASSO 2: Aguardar as opções do ComboBox aparecerem ---
        print("\n[INFO] Aguardando 2 segundos para as opções aparecerem...")
        time.sleep(2)

        # --- PASSO 3: Selecionar o vendedor ---
        # A lógica para definir o nome do vendedor pode ser ajustada aqui.
        # Por padrão, está usando o nome "AAAUTOMACAO" que você forneceu.
        vendedor_nome = "AAAUTOMACAO"
        print(f"[ACAO] Procurando e selecionando o vendedor: '{vendedor_nome}'...")

        try:
            app_top = app.top_window()
            item_text = app_top.child_window(title=vendedor_nome, control_type="Text", found_index=0)

            if item_text.exists():
                item_a_selecionar = item_text.parent()
                item_a_selecionar.set_focus()
                item_a_selecionar.click_input()
                print(f"[SUCESSO] Vendedor '{vendedor_nome}' selecionado.")
                return True
            else:
                print(f"[ERRO] Não foi possível encontrar o texto do vendedor '{vendedor_nome}' na lista.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar selecionar o vendedor: {e}")
            return False

    except ElementNotFoundError:
        print(f"[ERRO FATAL] O aplicativo '{APP_TITLE}' não foi encontrado. Ele está aberto?")
        return False
    except Exception as e:
        print(f"[ERRO INESPERADO] Ocorreu uma falha no módulo vendedor: {e}")
        return False
