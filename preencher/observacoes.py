# seu_projeto/preencher/observacoes.py (VERSÃO CORRETA E SIMPLIFICADA)
import pyautogui

def preencher(texto_da_observacao: str):
    """
    APENAS digita a observação, pois o cursor já está no lugar certo.
    """
    if not texto_da_observacao:
        print("AVISO: Texto de observação não fornecido. Pulando.")
        return

    print(f"Digitando Observação...")
    pyautogui.write(texto_da_observacao, interval=0.02)
    print("✅ Observação preenchida.")