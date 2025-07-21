# Home.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from PIL import Image
import os

st.set_page_config(page_title="Página Inicial", page_icon="🏠", layout="wide")
st.title("🏠 Página Inicial")

# ------------------------------------------------------------------
# --- Carrega dados do colaborador via API ---
# ------------------------------------------------------------------

@st.cache_data
def carregar_dados():
    url = "http://127.0.0.1:8000/dados"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Erro ao carregar dados.")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.stop()
# ------------------------------------------------------------------
# Simula a seleção do primeiro colaborador
# ------------------------------------------------------------------
colab = df.iloc[0]

# ------------------------------------------------------------------
# --- Layout da Home ---
# ------------------------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    imagem_path = "imgs/foto_padrao.png"
    if os.path.exists(imagem_path):
        st.image(imagem_path, width=180, caption=colab.get("Nome", "Colaborador"))

    st.markdown("### 📋 Dados Pessoais")
    campos = ["Nome", "Idade", "Empresa", "CPF", "Email"]
    for campo in campos:
        valor = colab.get(campo, "❓ Não informado")
        st.markdown(f"**{campo}:** {valor}")

with col2:
    st.markdown("### 📊 Visão Geral Rápida")
    # ------------------------------------------------------------------
    # --- Simulação de dados temporários para gráficos ---
    # ------------------------------------------------------------------
    df_salario = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "Salário Bruto": [3100, 3200, 3150, 3300, 3400, 3500]
    })

    df_horas = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "Horas Extras": [5, 3, 6, 4, 7, 2]
    })

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig1 = px.line(df_salario, x="Mês", y="Salário Bruto", title="Evolução do Salário Bruto", markers=True)
        fig1.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        fig2 = px.bar(df_horas, x="Mês", y="Horas Extras", title="Horas Extras por Mês")
        fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.success("Use o menu lateral para acessar o ChatBot, Visualizações e Insights.")
