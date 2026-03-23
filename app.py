import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agent.agente import rodar_agente

st.set_page_config(
    page_title="Agente Otimizador de Compras",
    page_icon="🛒",
    layout="centered"
)

st.markdown("""
<style>
    .block-container { max-width: 720px; padding-top: 2rem; }
    .produto-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        background: #fafafa;
    }
    .categoria-tag {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
        margin-bottom: 4px;
    }
    .produto-titulo {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .produto-preco {
        font-size: 22px;
        font-weight: 400;
        color: #1a1a1a;
    }
    .estrelas { color: #f0a500; font-size: 15px; }
    .review-texto {
        font-size: 13px;
        color: #555;
        line-height: 1.6;
        border-top: 1px solid #eee;
        padding-top: 10px;
        margin-top: 10px;
    }
    .metric-box {
        background: #f4f4f4;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-value { font-size: 22px; font-weight: 500; color: #1a1a1a; }
    .dica-box {
        background: #fffbea;
        border-left: 3px solid #f0a500;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 13px;
        color: #555;
        margin-top: 1rem;
    }
    .resumo-box {
        border-left: 3px solid #4a90d9;
        padding-left: 1rem;
        font-style: italic;
        color: #444;
        margin-bottom: 1.5rem;
        font-size: 15px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


def estrelas(nota):
    cheia = int(nota)
    meia = 1 if (nota % 1) >= 0.5 else 0
    vazia = 5 - cheia - meia
    return "★" * cheia + ("½" if meia else "") + "☆" * vazia


# --- Header ---
st.markdown("### 🛒 Agente Otimizador de Compras")
st.markdown(
    "<p style='color:#666;font-size:14px;margin-top:-8px'>"
    "Informe seu orçamento, os produtos que quer e as restrições. "
    "O agente encontra a melhor combinação automaticamente."
    "</p>",
    unsafe_allow_html=True
)

st.divider()


col1, col2 = st.columns([1, 2])
with col1:
    orcamento = st.number_input("Orçamento (R$)", min_value=1.0, value=500.0, step=50.0)
with col2:
    produtos_input = st.text_input(
        "Produtos desejados",
        placeholder="mouse, teclado, headset"
    )

restricoes_input = st.text_input(
    "Restrições (opcional)",
    placeholder="nota mínima 4.0, sem marcas genéricas, máx R$ 200 por item"
)

buscar = st.button("Otimizar compras ↗", type="primary", use_container_width=True)

# --- Execução ---
if buscar:
    if not produtos_input:
        st.warning("Informe pelo menos um produto desejado.")
    else:
        pedido = (
            f"Orçamento: R$ {orcamento:.2f}\n"
            f"Produtos desejados: {produtos_input}\n"
            f"Restrições: {restricoes_input or 'nenhuma'}"
        )

        with st.spinner("Agente trabalhando..."):
            etapas = st.empty()

            import time
            for etapa in [
                "🔍 Buscando produtos...",
                "🔧 Aplicando filtros...",
                "📐 Otimizando combinação...",
                "📝 Resumindo avaliações...",
            ]:
                etapas.info(etapa)
                time.sleep(0.5)

            etapas.empty()

            try:
                resposta = rodar_agente(pedido)
            except Exception as e:
                st.error(f"Erro ao executar o agente: {e}")
                st.stop()

        st.divider()
        st.markdown("#### Resultado")
        st.markdown(resposta)
