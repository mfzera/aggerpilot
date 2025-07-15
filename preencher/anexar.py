import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError

APP_TITLE = "AGGER GESTOR"
DIALOG_TITLE = "Abrir" # Título da janela de seleção de arquivo

def anexar(caminho_completo_pdf: str) -> bool:
    """
    Automatiza o processo de anexar um arquivo PDF na tela de prospecção.

    Esta função assume que a janela principal do Agger já está aberta e na
    tela correta onde o botão "INCLUIR ANEXOS" está visível.

    Args:
        caminho_completo_pdf (str): O caminho absoluto para o arquivo PDF
                                    que será anexado. Ex: "C:\\temp\\proposta.pdf"

    Returns:
        bool: True se o anexo foi realizado com sucesso, False caso contrário.
    """
    try:
        print(f"\n--- INICIANDO ANEXO DE PROPOSTA ---")
        print(f"[INFO] Anexando o arquivo: {caminho_completo_pdf}")

        # 1. Conectar-se à aplicação principal
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg_principal = app.window(title=APP_TITLE)
        dlg_principal.set_focus()

        # 2. Clicar no botão para abrir a janela de anexo
        # ATENÇÃO: O 'title' e 'control_type' podem precisar de ajuste.
        print("[ACAO] Procurando e clicando em 'INCLUIR ANEXOS'...")
        # Supondo que seja um botão. Se for um menu, o controle pode ser outro.
        btn_incluir_anexos = dlg_principal.child_window(title="INCLUIR ANEXOS", control_type="Button")
        if not btn_incluir_anexos.exists():
            print("🚨 ERRO: Botão 'INCLUIR ANEXOS' não encontrado.")
            return False
        btn_incluir_anexos.click_input()
        
        # 3. Esperar e conectar-se à nova janela "Abrir"
        print(f"[INFO] Aguardando a janela '{DIALOG_TITLE}' aparecer...")
        try:
            # Espera até 10 segundos pela janela de diálogo
            dlg_abrir = app.window(title=DIALOG_TITLE, timeout=10)
            dlg_abrir.wait('ready', timeout=10)
            print(f"[SUCESSO] Janela '{DIALOG_TITLE}' encontrada.")
        except TimeoutError:
            print(f"🚨 ERRO: A janela '{DIALOG_TITLE}' não apareceu a tempo.")
            return False

        # 4. Preencher o caminho do arquivo e confirmar
        # O campo de nome do arquivo geralmente é um ComboBox ou Edit
        print(f"[ACAO] Preenchendo o caminho do arquivo...")
        # Usamos type_keys para digitar o caminho completo.
        # 'with_spaces=True' garante que caminhos com espaços funcionem.
        dlg_abrir.type_keys(caminho_completo_pdf, with_spaces=True)
        time.sleep(1) # Pequena pausa para garantir que o texto foi digitado

        print("[ACAO] Clicando no botão 'Abrir' para confirmar...")
        btn_abrir = dlg_abrir.child_window(title="Abrir", control_type="Button")
        btn_abrir.click_input()

        print("✅ Anexo realizado com sucesso!")
        return True

    except ElementNotFoundError:
        print(f"🚨 ERRO FATAL: O aplicativo '{APP_TITLE}' não foi encontrado.")
        return False
    except Exception as e:
        print(f"🚨 ERRO INESPERADO durante o processo de anexo: {e}")
        return False
