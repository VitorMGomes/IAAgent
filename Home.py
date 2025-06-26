# Home.py
import streamlit as st
import pandas as pd
import requests
from PIL import Image
import os

# Configurações da página
st.set_page_config(page_title="Página Inicial", page_icon="🏠", layout="centered")
st.title("🏠 Página Inicial")

# Função para carregar dados do colaborador
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

# Simula a seleção do primeiro colaborador
colab = df.iloc[0]

# --- Exibe a imagem genérica ou personalizada ---
imagem_path = "imgs/foto_padrao.png"
if os.path.exists(imagem_path):
    st.image(imagem_path, width=180, caption=colab.get("Nome", "Colaborador"))

# --- Exibe os dados básicos ---
st.markdown("### 📋 Dados Pessoais")

colunas_desejadas = ["Nome", "Idade", "Empresa", "CPF", "Email"]
for campo in colunas_desejadas:
    valor = colab.get(campo, "❓ Não informado")
    st.markdown(f"**{campo}:** {valor}")

st.markdown("---")
st.success("Use o menu lateral para navegar entre o Chatbot, Visualizações e Insights.")
