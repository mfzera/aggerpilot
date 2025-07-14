from banco import buscar_cliente

def testar_buscar_cliente():
    resultado = buscar_cliente()
    
    if resultado:
        print("✅ Cliente encontrado:")
        for chave, valor in resultado.items():
            print(f"  {chave}: {valor}")
    else:
        print("❌ Nenhum cliente encontrado ou nome não extraído do PDF.")

if __name__ == "__main__":
    testar_buscar_cliente()
