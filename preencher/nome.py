from pywinauto import Application
import time

def preencher_nome(nome_cliente):
    print(f"👤 Preenchendo nome com: {nome_cliente}")

    app = Application(backend="uia").connect(title="AGGER GESTOR")
    janela = app.window(title="AGGER GESTOR")
    janela.set_focus()

    # Vamos listar TODOS os Custom
    customs = janela.descendants(control_type="Custom")

    if not customs:
        print("❌ Nenhum Custom encontrado!")
        return

    print(f"🔎 Encontrados {len(customs)} controles do tipo Custom:")
    for idx, custom in enumerate(customs):
        rect = custom.rectangle()
        print(f"  [{idx}] Custom Pos=({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")

    # Vamos tentar achar o que está na posição (40, 36, 1920, 1040)
    custom_container = None
    for custom in customs:
        rect = custom.rectangle()
        if rect.left == 40 and rect.top == 36 and rect.right == 1920 and rect.bottom == 1040:
            custom_container = custom
            print(f"✅ Achei o Custom container na posição {rect}")
            break

    if not custom_container:
        print("❌ Não achei o Custom certo. Verifique as coordenadas.")
        return

    # Para trabalhar com UIAWrapper, use .children() + filtro
    try:
        filhos = custom_container.children()

        # Debug - listar os filhos para saber quem é quem
        for i, filho in enumerate(filhos):
            print(f"[{i}] {filho.control_type()} - {filho.element_info.name} - auto_id={filho.element_info.automation_id}")

        # Procurar o ComboBox de PesquisaCliente
        combo_pesquisa = None
        for filho in filhos:
            if (filho.control_type() == "ComboBox" and 
                filho.element_info.automation_id == "PesquisaCliente"):
                combo_pesquisa = filho
                break

        if not combo_pesquisa:
            print("❌ Não achei o ComboBox de PesquisaCliente.")
            return

        combo_pesquisa.set_focus()
        combo_pesquisa.click_input()
        time.sleep(0.5)

        # Dentro do ComboBox, pegar o Edit
        filhos_combo = combo_pesquisa.children()
        edit_nome = None
        for filho in filhos_combo:
            if filho.control_type() == "Edit" and filho.element_info.automation_id == "Text":
                edit_nome = filho
                break

        if not edit_nome:
            print("❌ Não achei o Edit interno do ComboBox.")
            return

        edit_nome.set_edit_text(nome_cliente)
        print("✅ Nome preenchido com sucesso!")

    except Exception as e:
        print(f"⚠️ Erro ao acessar campo nome: {e}")

if __name__ == "__main__":
    preencher_nome("JOÃO DA SILVA")
