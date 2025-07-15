# seu_projeto/preencher/criar_tarefa.py
import pyautogui

# O nome da função deve ser 'selecionar' para bater com o que o orquestrador chama
def selecionar():
    """
    Pressiona Enter para marcar a caixa de seleção 'Criar tarefa'.
    """
    print("Selecionando 'Criar tarefa'...")
    pyautogui.press('enter')
    print("✅ 'Criar tarefa' selecionado.")