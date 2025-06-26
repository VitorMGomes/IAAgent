# 2_Insights_Personalizados.py
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Insights Personalizados", page_icon="📈")
st.title("📊 Insights Personalizados")
st.write("Aqui você verá os gráficos gerados automaticamente na conversa com o agente.")

# --- função local ---
def plot_insight(insight: dict):
    tipo = insight["tipo"]
    titulo = insight["titulo"]
    eixo_x = insight["eixo_x"]
    eixo_y = insight["eixo_y"]
    dados = insight["dados"]

    plt.figure(figsize=(8, 4))
    if tipo == "linha":
        plt.plot(eixo_x, dados, marker="o")
        plt.ylabel(eixo_y)
    elif tipo == "barra":
        plt.bar(eixo_x, dados)
        plt.ylabel(eixo_y)
    elif tipo == "pizza":
        labels = [item["label"] for item in dados]
        vals   = [item["value"] for item in dados]
        plt.pie(vals, labels=labels, autopct="%1.1f%%")
    plt.title(titulo)
    if tipo != "pizza":
        plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

# --- verifica se há insights ---
if "insights" not in st.session_state or not st.session_state.insights:
    st.info("Nenhum insight disponível. Volte ao chatbot e faça perguntas.")
    st.stop()

# --- itera sobre cada entrada de insight armazenada ---
for idx, wrapper in enumerate(st.session_state.insights, start=1):
    # wrapper = {"insights": [ {...}, {...} ]}
    insights = wrapper.get("insights", [])
    
    for insight in insights:
        st.markdown(f"### {idx}. {insight.get('titulo', '')}")
        with st.expander("🔍 Dados brutos"):
            st.json(insight)
        try:
            plot_insight(insight)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {e}")
        st.markdown("---")
