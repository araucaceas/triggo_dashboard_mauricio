import streamlit as st
import pandas as pd
import plotly.express as px
import gdown
import os

@st.cache_data
def baixar_e_carregar_csv(id_arquivo, nome_local):
    url = f"https://drive.google.com/uc?id={id_arquivo}"
    caminho = os.path.join("dados", nome_local)
    if not os.path.exists("dados"):
        os.makedirs("dados")
    if not os.path.exists(caminho):
        gdown.download(url, caminho, quiet=False)
    return pd.read_csv(caminho)

@st.cache_data
def carregar_todos_dados():
    orders = baixar_e_carregar_csv("1-EVul9TntgKPOA123VWFJl6NSgZ_X3aW", "olist_orders_dataset.csv")
    payments = baixar_e_carregar_csv("1YxuHVoOY_VxQq9V4Lqt9VWgAI1GP2OZr", "olist_order_payments_dataset.csv")
    items = baixar_e_carregar_csv("1j9pZAmJ5s6GCe4WY8EcCyXxx4w-2jRCE", "olist_order_items_dataset.csv")
    reviews = baixar_e_carregar_csv("1W9FzPK-u7ohUOLoS-RHi0XsUBD5xAwDj", "olist_order_reviews_dataset.csv")
    customers = baixar_e_carregar_csv("1Kqtpp7Z4yU7rb8AUXHZxGi_7iD0sU8-q", "olist_customers_dataset.csv")
    sellers = baixar_e_carregar_csv("1T9tfNFiLuWa4GV3w-DzS-5a1KMO4vkgN", "olist_sellers_dataset.csv")
    products = baixar_e_carregar_csv("1ZQPrh7NwWcTy1ewrBCczvxzckYv4PuHX", "olist_products_dataset.csv")
    geo = baixar_e_carregar_csv("1grhbfaN5Rcy8D5Zn3IG2uSCIP-0WUnZ2", "olist_geolocation_dataset.csv")
    category = baixar_e_carregar_csv("1-A5dbKeikqErPE0kfe3iykF8MVaXwja9", "product_category_name_translation.csv")
    return orders, payments, items, reviews, customers, sellers, products, geo, category

orders, payments, items, reviews, customers, sellers, products, geo, category = carregar_todos_dados()

st.set_page_config(layout="wide")
st.title("📦 Dashboard de Análise de Vendedores - Olist")

aba = st.sidebar.radio("Escolha uma aba", ["Visão Geral", "Análise de Vendedores", "Avaliações x Entrega"])

if aba == "Visão Geral":
    st.subheader("🔎 Visão Geral dos Dados")
    st.write("Total de pedidos:", orders["order_id"].nunique())
    st.write("Total de clientes:", customers["customer_unique_id"].nunique())
    st.write("Total de vendedores:", sellers["seller_id"].nunique())

elif aba == "Análise de Vendedores":
    st.subheader("🏬 Desempenho dos Vendedores")
    df = orders.merge(items, on="order_id").merge(sellers, on="seller_id")
    vendas_por_vendedor = df.groupby("seller_id")["order_id"].count().sort_values(ascending=False).head(10)
    st.plotly_chart(px.bar(vendas_por_vendedor, title="Top 10 Vendedores por Volume de Vendas"))

elif aba == "Avaliações x Entrega":
    st.subheader("📦 Relação entre Avaliação e Entrega")
    df = orders.merge(reviews, on="order_id")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["dias_entrega"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    fig = px.box(df, x="review_score", y="dias_entrega", points="all", title="Tempo de Entrega por Avaliação")
    st.plotly_chart(fig)

