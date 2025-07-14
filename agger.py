from pywinauto import Application
import time

def conectar_e_abrir_prospeccao():
    app = Application(backend="uia").connect(title_re=".*AGGER GESTOR.*")
    janela = app.window(title_re=".*AGGER GESTOR.*")
    janela.set_focus()

    print("✅ Conectado à janela principal AGGER GESTOR.")

    # Controles visíveis antes do clique
    controles_antes = set()
    for e in janela.descendants():
        if e.is_visible():
            controles_antes.add(e.element_info.runtime_id)

    # Clique no botão
    janela['CRIAR PROSPECÇÃO'].click_input()
    print("✅ Clique no botão 'CRIAR PROSPECÇÃO' realizado.")

    time.sleep(1)