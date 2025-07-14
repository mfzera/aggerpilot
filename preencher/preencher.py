# seu_projeto/preencher/preencher.py

"""
Módulo Orquestrador para Preenchimento com PyAutoGUI.
"""
import time
from . import nome, telefone, item, observacoes, vencimento, status, vendedor

def executar_preenchimento(dados_cliente: dict) -> bool:
    """
    Executa o fluxo completo de preenchimento de dados no sistema Agger
    usando PyAutoGUI.

    Args:
        dados_cliente (dict): Dicionário com os dados do cliente do banco.

    Returns:
        bool: True se o processo foi bem-sucedido, False caso contrário.
    """
    try:
        print("Iniciando o preenchimento com PyAutoGUI...")
        
        # O PyAutoGUI é muito rápido. Pausas ajudam o sistema a responder.
        time.sleep(2) 

        # Chama cada função na ordem correta, passando o dado específico.
        # Note que usamos as chaves do dicionário que o banco.py retorna.
        nome.preencher(dados_cliente.get('nome'))
        telefone.preencher(dados_cliente.get('telefone')) # Sempre será "0"
        item.preencher(dados_cliente.get('item'))
        observacoes.preencher(dados_cliente.get('observacao'))
        vencimento.preencher(dados_cliente.get('vigencia'))
        
        # Para os campos que são apenas cliques, não precisamos passar dados.
        status.selecionar(dados_cliente.get('status'))
        vendedor.selecionar(dados_cliente.get('vendedor'))
        
        print("✅ Preenchimento automatizado concluído com sucesso!")
        return True

    except Exception as e:
        print(f"🚨 ERRO: Falha durante a automação com PyAutoGUI.")
        print(f"Detalhe do erro: {e}")
        return False