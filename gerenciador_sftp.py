# Arquivo: gerenciador_sftp.py (VERSÃO CORRIGIDA E FINAL)

import paramiko
import os

class GerenciadorSFTP:
    """Uma classe para gerenciar a conexão e operações SFTP."""
    def __init__(self, config_ssh):
        self.ssh_client = None
        self.sftp_client = None
        self.config = config_ssh

    def conectar(self):
        """Estabelece laços de amizade com o servidor via SSH e SFTP."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(**self.config)
            self.sftp_client = self.ssh_client.open_sftp()
            print("✅ Conexão SFTP estabelecida com sucesso!")
        except Exception as e:
            print(f"❌ Falha ao conectar: {e}")
            raise

    def desconectar(self):
        """Fecha as conexões SFTP e SSH."""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        print("🔌 Conexões SFTP/SSH fechadas.")

    def listar_pdfs(self, caminho_remoto):
        """Lista todos os arquivos .pdf em um diretório remoto."""
        arquivos = self.sftp_client.listdir(caminho_remoto)
        return sorted([f for f in arquivos if f.lower().endswith(".pdf")])

    def baixar_arquivo(self, caminho_remoto, caminho_local):
        """Baixa um arquivo do servidor remoto para o caminho local."""
        self.sftp_client.get(caminho_remoto, caminho_local)
        print(f"⬇️ Arquivo baixado para: {caminho_local}")

    def remover_arquivo_remoto(self, caminho_remoto):
        """Remove um arquivo do servidor remoto."""
        self.sftp_client.remove(caminho_remoto)
        print(f"🗑️ Arquivo remoto deletado: {caminho_remoto}")

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()