# seu_projeto/preencher/telefone.py (VERSÃO SIMPLES - SÓ DIGITA)
import pyautogui

def preencher(numero_telefone: str):
    """
    APENAS digita o número do telefone, pois o cursor já está no lugar certo.
    """
    texto_para_escrever = str(numero_telefone)
    print(f"Digitando Telefone: '{texto_para_escrever}'...")
    pyautogui.write(texto_para_escrever, interval=0.05)
    print("✅ Telefone preenchido.")