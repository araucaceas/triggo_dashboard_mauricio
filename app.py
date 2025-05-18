import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise de Vendedores", layout="wide")

st.title("Dashboard de Vendedores - Olist")

# Carregar os dados
@st.cache_data
def carregar_dados():
    return pd.read_csv("resumo_vendedores.csv")

df = carregar_dados()

# Métricas principais
col1, col2, col3 = st.columns(3)
col1.metric("Total de Vendedores", df["seller_id"].nunique())
col2.metric("Média de Pedidos", f"{df['num_pedidos'].mean():.1f}")
col3.metric("Nota Média", f"{df['review_score'].mean():.2f}")

st.markdown("---")

# Gráficos
st.subheader("Volume de Pedidos por Vendedor")
fig1 = px.histogram(df, x="num_pedidos", nbins=30, title="Distribuição de Pedidos")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Satisfação dos Clientes (Review Score)")
fig2 = px.histogram(df, x="review_score", nbins=10, title="Distribuição de Notas")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Tempo Médio de Entrega por Vendedor")
fig3 = px.histogram(df, x="tempo_medio_entrega", nbins=30, title="Distribuição do Tempo de Entrega (dias)")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("Dados da Olist - Projeto de Análise por Mauricio Pinheiro")
