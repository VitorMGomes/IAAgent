import streamlit as st
import pandas as pd
import requests


@st.cache_data
def carregar_dados():
    url = "http://localhost:8000/dados"
    response = requests.get(url)
    if response.status_code == 200:
        dados_json = response.json()
        return pd.DataFrame(dados_json)
    else:
        st.error("Erro ao carregar dados da API.")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.stop()

meses_ordem = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_to_num = {mes: i+1 for i, mes in enumerate(meses_ordem)}
df["Mês"] = pd.Categorical(df["Mês"], categories=meses_ordem, ordered=True)
df["Data"] = pd.to_datetime(df["Ano"].astype(str) + "-" + df["Mês"].map(mes_to_num).astype(str) + "-01")
df = df.sort_values("Data")

st.title("Visualização Personalizada da Folha")

colunas_selecionadas = st.multiselect(
    "Selecione as colunas que deseja visualizar:",
    options=df.columns.tolist(),
    default=df.columns.tolist()[2:4]
)

if colunas_selecionadas:
    st.dataframe(df[colunas_selecionadas])
else:
    st.warning("Selecione ao menos uma coluna para visualizar os dados.")

st.subheader("📈 Evolução")

coluna_numerica = st.selectbox(
    "Selecione a coluna numérica para o gráfico:",
    options=[col for col in df.select_dtypes(include='number').columns if col != "Ano"]
)

datas_unicas = df["Data"].drop_duplicates().sort_values()
data_inicio, data_fim = st.select_slider(
    "Selecione o intervalo de tempo:",
    options=datas_unicas.tolist(),
    value=(datas_unicas.min(), datas_unicas.max()),
    format_func=lambda d: d.strftime("%B/%Y").capitalize()
)

filtro = df[(df["Data"] >= data_inicio) & (df["Data"] <= data_fim)]
df_agrupado = filtro.groupby("Data")[coluna_numerica].sum().reset_index()

st.line_chart(data=df_agrupado, x="Data", y=coluna_numerica)
