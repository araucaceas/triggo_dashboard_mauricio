import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("Dashboard Avançado - Análise de Dados Olist")

@st.cache_data
def carregar_dados():
    base_path = "C:/Users/arauc/Downloads/triggo"

    orders = pd.read_csv(os.path.join(base_path, "olist_orders_dataset.csv"))
    payments = pd.read_csv(os.path.join(base_path, "olist_order_payments_dataset.csv"))
    items = pd.read_csv(os.path.join(base_path, "olist_order_items_dataset.csv"))
    reviews = pd.read_csv(os.path.join(base_path, "olist_order_reviews_dataset.csv"))
    customers = pd.read_csv(os.path.join(base_path, "olist_customers_dataset.csv"))
    sellers = pd.read_csv(os.path.join(base_path, "olist_sellers_dataset.csv"))
    products = pd.read_csv(os.path.join(base_path, "olist_products_dataset.csv"))
    geo = pd.read_csv(os.path.join(base_path, "olist_geolocation_dataset.csv"))
    category = pd.read_csv(os.path.join(base_path, "product_category_name_translation.csv"))

    return orders, payments, items, reviews, customers, sellers, products, geo, category

# Carrega os dados
orders, payments, items, reviews, customers, sellers, products, geo, category = carregar_dados()

# Conversões de data
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])

# Merge dos dados essenciais
df = orders.merge(items, on="order_id")\
           .merge(products, on="product_id")\
           .merge(category, on="product_category_name", how="left")\
           .merge(customers, on="customer_id")\
           .merge(reviews, on="order_id", how="left")

# Extrair ano-mês para o gráfico de evolução
df["ano_mes"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

# Aba de seleção
aba = st.sidebar.radio("Escolha uma visualização", [
    "📊 Evolução de Vendas",
    "🗺️ Mapa de Calor por Estado",
    "📦 Avaliação vs Entrega",
    "🏆 Desempenho de Vendedores"
])

if aba == "📊 Evolução de Vendas":
    st.subheader("Evolução das Vendas ao Longo do Tempo")

    estados = st.multiselect("Filtrar por Estado:", options=df["customer_state"].unique(), default=df["customer_state"].unique())
    categorias = st.multiselect("Filtrar por Categoria de Produto:", options=category["product_category_name_english"].dropna().unique(), default=category["product_category_name_english"].dropna().unique())

    filtrado = df[(df["customer_state"].isin(estados)) & (df["product_category_name_english"].isin(categorias))]
    vendas_mensais = filtrado.groupby("ano_mes")["order_id"].count().reset_index(name="vendas")

    fig = px.line(vendas_mensais, x="ano_mes", y="vendas", markers=True, title="Vendas Mensais")
    st.plotly_chart(fig, use_container_width=True)

elif aba == "🗺️ Mapa de Calor por Estado":
    st.subheader("Concentração de Vendas por Estado")
    mapa = df.groupby("customer_state")["order_id"].count().reset_index(name="vendas")
    fig = px.choropleth(mapa, locations="customer_state", locationmode="USA-states",
                        color="vendas", scope="south america", title="Mapa de Vendas por Estado")
    st.plotly_chart(fig, use_container_width=True)

elif aba == "📦 Avaliação vs Entrega":
    st.subheader("Relação entre Avaliação e Tempo de Entrega")
    df["dias_entrega"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    aval_entrega = df.dropna(subset=["review_score", "dias_entrega"])
    fig = px.box(aval_entrega, x="review_score", y="dias_entrega", points="all", title="Tempo de Entrega por Nota de Avaliação")
    st.plotly_chart(fig, use_container_width=True)

elif aba == "🏆 Desempenho de Vendedores":
    st.subheader("Análise dos Vendedores")

    df_vend = df.copy()
    df_vend["dias_entrega"] = (df_vend["order_delivered_customer_date"] - df_vend["order_purchase_timestamp"]).dt.days

    desempenho = df_vend.groupby("seller_id").agg({
        "order_id": "count",
        "review_score": "mean",
        "dias_entrega": "mean"
    }).reset_index().rename(columns={
        "order_id": "vendas",
        "review_score": "satisfacao_media",
        "dias_entrega": "tempo_medio_entrega"
    })

    top = desempenho.sort_values(by="vendas", ascending=False).head(10)
    st.dataframe(top)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(top, x="seller_id", y="vendas", title="Top 10 Vendedores - Volume de Vendas"), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(top, x="seller_id", y="satisfacao_media", title="Top 10 Vendedores - Satisfação Média"), use_container_width=True)

st.caption("📊 Projeto por Mauricio Pinheiro | Dados Triggo")
