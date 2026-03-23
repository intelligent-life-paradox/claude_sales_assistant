TOOLS_SCHEMA = [
    {
        "name": "buscar_produtos",
        "description": (
            "Busca produtos em uma categoria específica (ex: 'mouse gamer', "
            "'teclado mecânico', 'headset'). Retorna lista com título, preço, "
            "avaliação, número de avaliações, ASIN e link."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query":  {"type": "string",  "description": "Termo de busca do produto"},
                "limite": {"type": "integer", "description": "Máximo de resultados (padrão: 8)", "default": 8},
            },
            "required": ["query"],
        },
    },
    {
        "name": "aplicar_filtros",
        "description": (
            "Filtra uma lista de produtos de acordo com as restrições do usuário, "
            "como avaliação mínima, preço máximo por item, marcas excluídas e "
            "número mínimo de avaliações."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "produtos": {
                    "type": "array",
                    "description": "Lista de produtos retornada por buscar_produtos"
                },
                "restricoes": {
                    "type": "object",
                    "description": (
                        "Objeto com restrições opcionais: "
                        "avaliacao_minima (float), "
                        "preco_maximo_por_item (float), "
                        "marcas_excluidas (list[str]), "
                        "avaliacoes_minimas (int)"
                    ),
                },
            },
            "required": ["produtos", "restricoes"],
        },
    },
    {
        "name": "otimizar_compras",
        "description": (
            "Usa Programação Linear para selecionar a melhor combinação de produtos "
            "dentro do orçamento. Maximiza avaliação e minimiza preço ao mesmo tempo. "
            "Garante no máximo 1 produto por categoria."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "produtos": {
                    "type": "array",
                    "description": "Lista de produtos já filtrados, cada um com campo 'categoria'"
                },
                "orcamento": {
                    "type": "number",
                    "description": "Orçamento total disponível em reais"
                },
                "peso_avaliacao": {
                    "type": "number",
                    "description": "Peso da avaliação na função objetivo (padrão: 10.0)",
                    "default": 10.0
                },
                "peso_preco": {
                    "type": "number",
                    "description": "Peso do preço na penalização (padrão: 0.01)",
                    "default": 0.01
                },
            },
            "required": ["produtos", "orcamento"],
        },
    },
    {
        "name": "buscar_reviews",
        "description": (
            "Busca reviews reais de um produto pelo ASIN da Amazon. "
            "Retorna: sentimento geral (escala de Muito positivo a Muito negativo), "
            "melhor review positivo e melhor review negativo com texto, usuário e data. "
            "Use esta tool para cada produto selecionado pelo otimizador."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "asin":  {"type": "string",  "description": "ASIN do produto na Amazon"},
                "limite": {"type": "integer", "description": "Número de reviews a analisar (padrão: 5)", "default": 5},
            },
            "required": ["asin"],
        },
    },
]