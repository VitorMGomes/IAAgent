# 2_Insights_Personalizados.py
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Insights Personalizados", page_icon="📈")
st.title("📊 Insights Personalizados")
st.write("Aqui você verá os gráficos gerados automaticamente na conversa com o agente.")

# --- função local com PLOTLY ---
def plot_insight(insight: dict):
    tipo = insight["tipo"]
    titulo = insight["titulo"]
    eixo_x = insight["eixo_x"]
    eixo_y = insight["eixo_y"]
    dados = insight["dados"]

    fig = None

    if tipo == "linha":
        fig = go.Figure(data=go.Scatter(x=eixo_x, y=dados, mode="lines+markers"))
        fig.update_layout(title=titulo, xaxis_title="", yaxis_title=eixo_y)

    elif tipo == "barra":
        fig = go.Figure(data=go.Bar(x=eixo_x, y=dados))
        fig.update_layout(title=titulo, xaxis_title="", yaxis_title=eixo_y)

    elif tipo == "pizza":
        labels = [item["label"] for item in dados]
        values = [item["value"] for item in dados]
        fig = go.Figure(data=go.Pie(labels=labels, values=values, hole=0.3))
        fig.update_layout(title=titulo)

    if fig:
        fig.update_layout(margin=dict(t=40, b=40, l=20, r=20), height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- verifica se há insights ---
if "insights" not in st.session_state or not st.session_state.insights:
    st.info("Nenhum insight disponível. Volte ao chatbot e faça perguntas.")
    st.stop()

# --- itera sobre cada entrada de insight armazenada ---
for idx, wrapper in enumerate(st.session_state.insights, start=1):
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
