from banco import buscar_cliente

dados_cliente = buscar_cliente()

if dados_cliente:
    nome = dados_cliente["nome"]
    item = dados_cliente["item"]

    print(f"Nome: {nome}")
    print(f"Item: {item}")
else:
    print("Cliente não encontrado.")
