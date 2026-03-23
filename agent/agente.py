import json
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import anthropic
from dotenv import load_dotenv

from tools.busca      import buscar_produtos, buscar_reviews
from tools.otimizador import aplicar_filtros, otimizar_compras
from agent.tools_schema import TOOLS_SCHEMA

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Você é um agente especialista em otimização de compras.

[MANDATÓRIO] Siga este fluxo de trabalho:

1. Interpretar o pedido do usuário: orçamento, categorias desejadas e restrições.
2. Para cada categoria, chamar buscar_produtos.
3. Adicionar o campo "categoria" em cada produto retornado (use o nome da categoria).
4. Chamar aplicar_filtros com todos os produtos e as restrições do usuário.
   - Se o usuário não informar restrições, passe restricoes={}.
5. Chamar otimizar_compras com os produtos filtrados e o orçamento total.
6. Para cada produto selecionado, chamar buscar_reviews passando o campo "asin" do produto.
7. Apresentar o resultado final de forma clara com:

   Para cada produto:
   - Nome, preço e link
   - Sentimento geral das reviews (escala: Muito positivo para Muito negativo)
   - Melhor comentário POSITIVO: texto completo, usuário e data
   - Melhor comentário NEGATIVO: texto completo, usuário e data
   - Se não houver comentário negativo, informe que não foram encontrados negativos

   No final:
   - Total gasto e quanto sobrou do orçamento
   - Explicação de por que essa combinação é a melhor

[IMPORTANTE]
Seja direto e útil. Não invente dados — use apenas o que as tools retornam.
Se buscar_reviews retornar erro, informe o usuário e continue com os outros produtos."""


def executar_tool(nome: str, argumentos: dict) -> str:
    """Executa a tool correta e retorna o resultado como JSON string."""
    print(f"\n[tool] {nome}({list(argumentos.keys())})")

    if nome == "buscar_produtos":
        resultado = buscar_produtos(**argumentos)

    elif nome == "aplicar_filtros":
        resultado = aplicar_filtros(**argumentos)

    elif nome == "otimizar_compras":
        resultado = otimizar_compras(**argumentos)

    elif nome == "buscar_reviews":
        resultado = buscar_reviews(**argumentos)

    else:
        resultado = {"erro": f"Tool desconhecida: {nome}"}

    return json.dumps(resultado, ensure_ascii=False)


def rodar_agente(pedido_usuario: str) -> str:
    """Loop principal do agente — continua até stop_reason ser end_turn."""
    print(f"\n{'='*10}")
    print(f"Pedido: {pedido_usuario}")
    print('='*10)

    mensagens = [{"role": "user", "content": pedido_usuario}]

    while True:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS_SCHEMA,
            messages=mensagens,
        )

        mensagens.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            for bloco in resp.content:
                if hasattr(bloco, "text"):
                    return bloco.text
            return "Sem resposta textual."

        if resp.stop_reason == "tool_use":
            resultados_tools = []

            for bloco in resp.content:
                if bloco.type == "tool_use":
                    resultado = executar_tool(bloco.name, bloco.input)
                    resultados_tools.append({
                        "type":        "tool_result",
                        "tool_use_id": bloco.id,
                        "content":     resultado,
                    })

            mensagens.append({"role": "user", "content": resultados_tools})

        else:
            break

    return "Agente encerrou sem resposta final."