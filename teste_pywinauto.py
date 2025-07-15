# Arquivo: teste_pywinauto.py (Versão que salva em arquivo)

from pywinauto.application import Application
import time
import os

# Título exato da janela
TITULO_DA_JANELA = "AGGER GESTOR"
# Nome do arquivo que vamos criar
NOME_ARQUIVO_SAIDA = "mapa_de_controles.txt"

print(f"Tentando se conectar à janela com o título: '{TITULO_DA_JANELA}'")
time.sleep(2)

try:
    app = Application(backend="uia").connect(title=TITULO_DA_JANELA, timeout=10)
    janela_principal = app.window(title=TITULO_DA_JANELA)

    print("\n✅ Conexão bem-sucedida!")
    print(f"Salvando a árvore de controles no arquivo: '{NOME_ARQUIVO_SAIDA}'...")
    
    # A MÁGICA ACONTECE AQUI:
    # Passamos o nome do arquivo diretamente para a função.
    janela_principal.print_control_identifiers(filename=NOME_ARQUIVO_SAIDA)
    
    # Pega o caminho completo do arquivo para mostrar ao usuário
    caminho_completo = os.path.abspath(NOME_ARQUIVO_SAIDA)
    print(f"\n✅ Mapa de controles salvo com sucesso em:")
    print(f"   {caminho_completo}")
    print("\nAbra este arquivo de texto para ver a lista completa de controles.")

except Exception as e:
    print(f"🚨 ERRO: Não foi possível se conectar à janela.")
    print(f"   Verifique se o título '{TITULO_DA_JANELA}' está exatamente correto.")
    print(f"   Detalhe do erro: {e}")