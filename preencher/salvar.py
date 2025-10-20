# Arquivo: preencher/salvar.py (VERSÃO CORRIGIDA COM INVOKE)

import time
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError

APP_TITLE = "AGGER GESTOR"

def salvar_prospeccao() -> bool:
    """
    Encontra e clica no botão 'SALVAR' para finalizar e salvar a prospecção.
    Assume que a janela principal do Agger já está aberta e na tela correta.

    Returns:
        bool: True se o clique em Salvar foi bem-sucedido, False caso contrário.
    """
    print("\n--- INICIANDO ETAPA DE SALVAR ---")
    try:
        print("[INFO] Conectando ao app AGGER GESTOR para salvar...")
        # Conecta-se e foca na janela
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=10)
        dlg = app.window(title=APP_TITLE)
        dlg.set_focus()

        print("[ACAO] Procurando o botão 'SALVAR'...")
        # Encontra o botão Salvar
        salvar_button = dlg.child_window(auto_id="SalvarButton", control_type="MenuItem")

        print("[INFO] Aguardando o botão 'SALVAR' ficar visível e ativo...")
        salvar_button.wait('visible enabled', timeout=15) # Espera até estar pronto
        print("[SUCESSO] Botão 'SALVAR' encontrado e pronto.")

        # --- CORREÇÃO: Uso do invoke() para um clique mais robusto ---
        salvar_button.invoke() # Invoca a ação de clique diretamente
        time.sleep(0.5) # Pausa mínima para garantir que o comando foi processado
        
        print("[SUCESSO] Comando 'Salvar' (invoke) realizado.")
        
        # Adiciona uma pausa para o sistema processar o salvamento e fechar a janela.
        print("[INFO] Aguardando 3 segundos para a operação de salvar ser concluída...")
        time.sleep(3)
        
        return True

    except (ElementNotFoundError, TimeoutError) as e:
        print(f"🚨 ERRO: Não foi possível encontrar ou invocar 'SALVAR': {e}")
        return False
    except Exception as e:
        print(f"🚨 ERRO INESPERADO ao tentar salvar a prospecção: {e}")
        return False