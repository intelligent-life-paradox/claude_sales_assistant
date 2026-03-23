from agent.agente import rodar_agente

def main():
    print("\n Agente Otimizador para suas Compras ⭐")
    print("Digite seu pedido em linguagem natural.")
    print("Exemplos:")
    print("  'Tenho R$ 500 para mouse, teclado e headset'")
    print("  'Quero montar um kit home office com R$ 800, só produtos com nota acima de 4'")
    print("  'R$ 300 para mouse e teclado, sem marcas genéricas'\n")

    pedido = input("Seu pedido: ").strip()

    if not pedido:
        print("Nenhum pedido informado.")
        return

    resposta = rodar_agente(pedido)

    print("\n")
    print("RESULTADO FINAL:")
    print(resposta)


if __name__ == "__main__":
    main()
