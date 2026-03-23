from busca import buscar_produtos

for categoria in ["mouse gamer", "teclado mecanico", "headset"]:
    print(f"\n=== {categoria.upper()} ===")
    for p in buscar_produtos(categoria, limite=3):
        print(f"  {p['titulo'][:45]}")
        print(f"  R$ {p['preco']:.2f} | ⭐ {p['avaliacao']}")
        print()