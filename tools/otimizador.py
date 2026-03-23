from pulp import LpProblem, LpVariable, LpMaximize, lpSum, value, PULP_CBC_CMD


def aplicar_filtros(produtos: list, restricoes: dict) -> list:
    filtrados = []
    av_min    = restricoes.get("avaliacao_minima", 0)
    preco_max = restricoes.get("preco_maximo_por_item", float("inf"))
    marcas_exc = [m.lower() for m in restricoes.get("marcas_excluidas", [])]
    num_min   = restricoes.get("avaliacoes_minimas", 0)

    for p in produtos:
        if p.get("avaliacao", 0) < av_min:
            continue
        if p.get("preco", 0) > preco_max:
            continue
        if p.get("num_avaliacoes", 0) < num_min:
            continue
        titulo_lower = p.get("titulo", "").lower()
        if any(marca in titulo_lower for marca in marcas_exc):
            continue
        filtrados.append(p)

    return filtrados


def otimizar_compras(produtos: list, orcamento: float,
                     peso_avaliacao: float = 10.0,
                     peso_preco: float = 0.01) -> dict:

    # garante que todos os produtos têm os campos necessários
    for p in produtos:
        p.setdefault("avaliacao", 0.0)
        p.setdefault("num_avaliacoes", 0)
        p.setdefault("preco", 0.0)
        p.setdefault("titulo", "Produto sem nome")
        p.setdefault("link", "")
        p.setdefault("categoria", "geral")

    # remove produtos sem preço válido
    produtos = [p for p in produtos if p["preco"] > 0]

    if not produtos:
        return {
            "selecionados": [],
            "total": 0.0,
            "avaliacao_media": 0.0,
            "sobrou": orcamento,
            "erro": "Nenhum produto encontrado após os filtros."
        }

    # verifica se algum produto individual cabe no orçamento
    cabem = [p for p in produtos if p["preco"] <= orcamento]
    if not cabem:
        menor = min(produtos, key=lambda p: p["preco"])
        return {
            "selecionados": [],
            "total": 0.0,
            "avaliacao_media": 0.0,
            "sobrou": orcamento,
            "erro": (
                f"Orçamento insuficiente. "
                f"O produto mais barato encontrado é '{menor['titulo']}' "
                f"por R$ {menor['preco']:.2f}. "
                f"Você precisaria de pelo menos R$ {menor['preco']:.2f}."
            )
        }

    preco_max_val = max(p["preco"] for p in produtos) or 1
    av_max        = max(p["avaliacao"] for p in produtos) or 1

    prob = LpProblem("otimizar_compras", LpMaximize)
    n = len(produtos)
    x = [LpVariable(f"x{i}", cat="Binary") for i in range(n)]

    prob += lpSum(
        x[i] * (
            (produtos[i]["avaliacao"] / av_max) * peso_avaliacao
            - (produtos[i]["preco"] / preco_max_val) * peso_preco
        )
        for i in range(n)
    )

    prob += lpSum(x[i] * produtos[i]["preco"] for i in range(n)) <= orcamento

    categorias = {}
    for i, p in enumerate(produtos):
        cat = p.get("categoria", "geral")
        categorias.setdefault(cat, []).append(i)
    for indices in categorias.values():
        prob += lpSum(x[i] for i in indices) <= 1

    prob.solve(PULP_CBC_CMD(msg=0))

    selecionados = [produtos[i] for i in range(n) if value(x[i]) == 1]
    total    = sum(p["preco"] for p in selecionados)
    av_media = (
        sum(p["avaliacao"] for p in selecionados) / len(selecionados)
        if selecionados else 0.0
    )

    return {
        "selecionados":    selecionados,
        "total":           round(total, 2),
        "avaliacao_media": round(av_media, 2),
        "sobrou":          round(orcamento - total, 2),
    }