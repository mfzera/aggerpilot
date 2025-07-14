from banco import buscar_cliente
from consultar import extrair_nome_primeiro_pdf

def main():
    # Testa extrair nome do PDF
    nome_pdf = extrair_nome_primeiro_pdf()
    print(f"Nome extraído do PDF: {nome_pdf}")

    # Testa buscar cliente no banco pelo nome extraído
    dados = buscar_cliente()
    if dados:
        print("Dados do cliente encontrados:")
        print(dados)
    else:
        print("Cliente não encontrado no banco.")

if __name__ == "__main__":
    main()
