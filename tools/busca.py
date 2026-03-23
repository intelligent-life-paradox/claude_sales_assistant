import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")



# AMAZON


def buscar_amazon(query: str, limite: int = 8) -> list:
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key":  RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    params = {"query": query, "country": "BR", "page": "1"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[amazon] Erro: {e}")
        return []

    produtos = []
    for item in dados.get("data", {}).get("products", [])[:limite]:
        preco = _parse_preco(item.get("product_price"))
        avaliacao = _parse_float(item.get("product_star_rating"))
        num_av = _parse_int(item.get("product_num_ratings"))
        if preco > 0:
            produtos.append({
                "asin":           item.get("asin", ""),
                "titulo":         item.get("product_title", "")[:80],
                "preco":          preco,
                "avaliacao":      avaliacao,
                "num_avaliacoes": num_av,
                "link":           item.get("product_url", ""),
                "site":           "Amazon",
            })
    return produtos


def buscar_reviews(asin: str, limite: int = 5) -> dict:
    """Busca reviews reais de um produto pelo ASIN da Amazon."""
    if not asin:
        return {"erro": "ASIN não informado."}

    url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"
    headers = {
        "X-RapidAPI-Key":  RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    params = {
        "asin":    asin,
        "country": "BR",
        "page":    "1",
        "star_rating": "ALL",
        "sort_by": "TOP_REVIEWS",
        "verified_purchases_only": "false",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
    except requests.exceptions.RequestException as e:
        return {"erro": f"Erro ao buscar reviews: {e}"}

    reviews_raw = dados.get("data", {}).get("reviews", [])[:limite]
    if not reviews_raw:
        return {"erro": "Nenhuma review encontrada."}

    reviews = []
    for r in reviews_raw:
        nota = _parse_float(r.get("review_star_rating"))
        reviews.append({
            "usuario": r.get("review_author", "Anônimo"),
            "data":    r.get("review_date", "data desconhecida"),
            "nota":    nota,
            "titulo":  r.get("review_title", ""),
            "texto":   r.get("review_comment", ""),
            "positivo": nota >= 4.0,
        })

    media = sum(r["nota"] for r in reviews) / len(reviews) if reviews else 0
    sentimento = (
        "Muito positivo" if media >= 4.5 else
        "Positivo"       if media >= 3.5 else
        "Neutro"         if media >= 2.5 else
        "Negativo"       if media >= 1.5 else
        "Muito negativo"
    )

    positivos = [r for r in reviews if r["positivo"] and r["texto"]]
    negativos = [r for r in reviews if not r["positivo"] and r["texto"]]

    return {
        "sentimento":       sentimento,
        "media_reviews":    round(media, 1),
        "total_analisadas": len(reviews),
        "melhor_positivo":  max(positivos, key=lambda r: len(r["texto"])) if positivos else None,
        "melhor_negativo":  max(negativos, key=lambda r: len(r["texto"])) if negativos else None,
    }



# EBAY


def buscar_ebay(query: str, limite: int = 8) -> list:
    url = "https://ebay-product-search.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key":  RAPIDAPI_KEY,
        "X-RapidAPI-Host": "ebay-product-search.p.rapidapi.com"
    }
    params = {"q": query, "country": "BR"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[ebay] Erro: {e}")
        return []

    produtos = []
    for item in (dados.get("results") or dados.get("data", {}).get("results", []))[:limite]:
        preco = _parse_preco(
            item.get("price") or
            item.get("currentPrice") or
            item.get("priceInfo", {}).get("price")
        )
        avaliacao = _parse_float(item.get("rating") or item.get("averageRating"))
        num_av    = _parse_int(item.get("reviewCount") or item.get("numReviews"))
        titulo    = item.get("title") or item.get("name", "")
        link      = item.get("url") or item.get("link") or item.get("itemUrl", "")

        if preco > 0:
            produtos.append({
                "asin":           "",
                "titulo":         titulo[:80],
                "preco":          preco,
                "avaliacao":      avaliacao,
                "num_avaliacoes": num_av,
                "link":           link,
                "site":           "eBay",
            })
    return produtos



# ALIEXPRESS


def buscar_aliexpress(query: str, limite: int = 8) -> list:
    url = "https://aliexpress-datahub.p.rapidapi.com/item_search_2"
    headers = {
        "X-RapidAPI-Key":  RAPIDAPI_KEY,
        "X-RapidAPI-Host": "aliexpress-datahub.p.rapidapi.com"
    }
    params = {"q": query, "page": "1", "sort": "default"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[aliexpress] Erro: {e}")
        return []

    items = (
        dados.get("result", {}).get("resultList") or
        dados.get("resultList") or
        []
    )

    produtos = []
    for entry in items[:limite]:
        item = entry.get("item", entry)
        preco     = _parse_float(item.get("promotionPrice") or item.get("price"))
        avaliacao = _parse_float(item.get("averageStarRate") or item.get("starRate"))
        num_av    = _parse_int(item.get("evaluate") or item.get("evaluateCount"))
        titulo    = item.get("title", "")
        link      = item.get("itemUrl") or item.get("detailUrl", "")
        if link and not link.startswith("http"):
            link = "https:" + link

        if preco > 0:
            produtos.append({
                "asin":           "",
                "titulo":         titulo[:80],
                "preco":          preco,
                "avaliacao":      avaliacao,
                "num_avaliacoes": num_av,
                "link":           link,
                "site":           "AliExpress",
            })
    return produtos



# AGREGADOR (aqui a gente chama os 3)


def buscar_produtos(query: str, limite: int = 8) -> list:
    """Busca em Amazon, eBay e AliExpress e agrega os resultados."""
    todos = []

    for fn, nome in [
        (buscar_amazon,     "Amazon"),
        (buscar_ebay,       "eBay"),
        (buscar_aliexpress, "AliExpress"),
    ]:
        try:
            resultados = fn(query, limite)
            print(f"[{nome}] {len(resultados)} produtos encontrados")
            todos.extend(resultados)
        except Exception as e:
            print(f"[{nome}] falhou: {e}")

    return todos





def _parse_preco(raw) -> float:
    if raw is None:
        return 0.0
    try:
        return float(
            str(raw)
            .replace("R$", "").replace("$", "").replace("US", "")
            .replace(".", "").replace(",", ".").strip()
        )
    except ValueError:
        return 0.0


def _parse_float(raw) -> float:
    if raw is None:
        return 0.0
    try:
        return float(str(raw).replace(",", ".").strip())
    except ValueError:
        return 0.0


def _parse_int(raw) -> int:
    if raw is None:
        return 0
    try:
        return int(str(raw).replace(".", "").replace(",", "").strip())
    except ValueError:
        return 0