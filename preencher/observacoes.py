import pyautogui
import pyperclip
import time

def preencher(dados_cliente: dict):
    """
    Preenche o campo de observações com um texto formatado
    contendo múltiplos detalhes do cliente.

    Args:
        dados_cliente (dict): Dicionário completo com os dados do cliente.
    """
    print("Formatando e preenchendo o campo de Observação...")
    try:
        # Extrai os dados do dicionário, com valores padrão para segurança
        vendedor = dados_cliente.get('vendedor', 'N/A')
        situacao = dados_cliente.get('situacao', 'N/A')
        observacao_original = dados_cliente.get('observacao', 'N/A')
        
        # --- LÓGICA DE FORMATAÇÃO DA COMISSÃO ---
        comissao_decimal = dados_cliente.get('pct_atual')
        comissao_formatada = "N/A" # Valor padrão
        
        if isinstance(comissao_decimal, (int, float)):
            # Converte o decimal para porcentagem (ex: 0.22 -> 22%)
            porcentagem = int(comissao_decimal * 100)
            comissao_formatada = f"{porcentagem}%"
        
        # Monta o texto formatado com quebras de linha
        texto_formatado = (
            f"{vendedor} - VENDEDOR\n"
            f"{comissao_formatada} - COMISSAO\n"
            f"{situacao} - SITUACAO\n"
            f"{observacao_original} - OBSERVAÇÃO"
        )

        # Usar pyperclip para lidar com texto multi-linha e caracteres especiais é mais seguro
        pyperclip.copy(texto_formatado)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        
        print("✅ Observação formatada e preenchida.")
        
    except Exception as e:
        print(f"🚨 ERRO ao preencher o campo de observações: {e}")
