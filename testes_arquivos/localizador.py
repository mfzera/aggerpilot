from pywinauto import Application
import time

def mapear_visiveis_pos_clique():
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

    # Controles visíveis depois do clique
    controles_depois = []
    for e in janela.descendants():
        if e.is_visible():
            controles_depois.append(e)

    # Filtra controles que ficaram visíveis só depois do clique
    novos_visiveis = [e for e in controles_depois if e.element_info.runtime_id not in controles_antes]

    print(f"\n🔎 Novos controles visíveis após o clique: {len(novos_visiveis)}")

    with open("novos_controles_visiveis.txt", "w", encoding="utf-8") as f:
        for e in novos_visiveis:
            linha = f"{e.friendly_class_name()} | Name: {e.window_text()} | AutomationId: {e.automation_id()}"
            print(linha)
            f.write(linha + "\n")

    print("\n✅ Mapeamento salvo em 'novos_controles_visiveis.txt'.")

if __name__ == "__main__":
    mapear_visiveis_pos_clique()
