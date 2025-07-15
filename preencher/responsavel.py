import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

APP_TITLE = "AGGER GESTOR"

def selecionar_responsavel(situacao: str) -> bool:
    """
    Conecta-se ao aplicativo AGGER GESTOR, que já deve estar aberto e focado
    na tela de prospecção, para selecionar o responsável.

    Args:
        situacao (str): A situação do cadastro (ex: "CANCELADO", "ATIVO").
                        Determina qual responsável será selecionado.

    Returns:
        bool: True se o responsável foi selecionado com sucesso, False caso contrário.
    """
    try:
        print(f"[INFO] Módulo Responsável: Conectando ao app '{APP_TITLE}'...")
        # Conecta-se à aplicação que já está em execução
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)

        # Garante que a janela está pronta para receber inputs
        dlg.set_focus()
        dlg.wait("ready", timeout=10)
        
        print("[INFO] Módulo Responsável: Janela principal focada.")

        # --- PASSO 1: Clicar no ComboBox "Responsável" ---
        print("[ACAO] Procurando e clicando no ComboBox de 'Responsável'...")
        try:
            # Tenta encontrar o ComboBox pelo índice. Este valor pode precisar de ajuste.
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
        print("\n[INFO] Aguardando 1 segundo para as opções aparecerem...")
        time.sleep(1)

        # --- PASSO 3: Selecionar o responsável com base na condição ---
        print(f"[INFO] A situação recebida é: '{situacao}'")

        responsavel_nome = ""
        if situacao and situacao.lower() == "cancelado":
            responsavel_nome = "MARIA JOSE"
        else:
            responsavel_nome = "BARBARA"

        print(f"[ACAO] Procurando e selecionando o responsável: '{responsavel_nome}'...")

        try:
            # A lista de opções aparece em uma nova janela/painel, então buscamos a partir do topo.
            app_top = app.top_window()
            item_text = app_top.child_window(title=responsavel_nome, control_type="Text", found_index=0)

            if item_text.exists():
                # Pega o "pai" do texto, que é o ListItem clicável.
                item_a_selecionar = item_text.parent()
                item_a_selecionar.click_input()
                print(f"[SUCESSO] Responsável '{responsavel_nome}' selecionado.")
                return True
            else:
                print(f"[ERRO] Não foi possível encontrar o texto do responsável '{responsavel_nome}' na lista.")
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao tentar selecionar o responsável: {e}")
            return False

    except ElementNotFoundError:
        print(f"[ERRO FATAL] O aplicativo '{APP_TITLE}' não foi encontrado. Ele está aberto?")
        return False
    except Exception as e:
        print(f"[ERRO INESPERADO] Ocorreu uma falha no módulo responsável: {e}")
        return False
