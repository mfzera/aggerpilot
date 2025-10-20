# Arquivo: agger.py (VERSÃO OTIMIZADA PARA VELOCIDADE)

from pywinauto import Application
import time

def conectar_e_abrir_prospeccao():
    """
    Conecta-se à janela do AGGER e clica no botão 'CRIAR PROSPECÇÃO'
    de forma otimizada.
    """
    try:
        # A conexão por 'title_re' é necessária, mas o tempo pode variar.
        # Mantemos o backend 'uia' que é mais robusto para controles modernos.
        app = Application(backend="uia").connect(title_re=".*AGGER GESTOR.*")
        janela = app.window(title_re=".*AGGER GESTOR.*")
        
        # Garante que a janela está ativa e pronta para cliques
        janela.set_focus()
        janela.wait('ready', timeout=5) # Adiciona um wait explícito para 'ready' para maior estabilidade
        
        print("✅ Conectado e janela principal AGGER GESTOR focada.")

        # Clique no botão (Use 'click_input' ou 'click()', dependendo do que for mais rápido/estável)
        # Se o clique for o lento, podemos tentar 'click()' puro, mas 'click_input()' é geralmente mais confiável.
        janela['CRIAR PROSPECÇÃO'].click_input()
        print("✅ Clique no botão 'CRIAR PROSPECÇÃO' realizado.")

        # Uma pausa mínima após a ação é boa prática
        time.sleep(1)
        
    except Exception as e:
        print(f"🚨 ERRO ao tentar conectar ou clicar no botão: {e}")
        # Você pode querer levantar a exceção aqui se for um erro crítico.