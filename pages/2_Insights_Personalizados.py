import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Insights Personalizados", page_icon="📈")
st.title("📊 Insights Personalizados")
st.write("Aqui você verá os gráficos e análises gerados automaticamente enquanto conversa com o agente.")

# Verificação de existência de insights
if "insights" not in st.session_state or not st.session_state.insights:
    st.info("Nenhum insight foi gerado ainda. Volte ao chatbot e faça uma pergunta.")
    st.stop()

# Renderiza todos os insights acumulados
for i, insight in enumerate(st.session_state.insights, 1):
    st.markdown(f"### {i}. {insight['titulo']}")

    # Expansor para depuração
    with st.expander("🔍 Ver dados brutos do insight", expanded=False):
        st.json(insight)

    # Tipo texto
    if insight["tipo"] == "texto":
        st.markdown(insight["conteudo"])

    # Tipo gráfico
    elif insight["tipo"] in {"grafico_barras", "grafico_linha", "grafico_pizza"}:
        try:
            df = pd.DataFrame(insight["dados"])

            # Mostra tabela para referência
            with st.expander("📋 Tabela de dados utilizada", expanded=False):
                st.dataframe(df)

            # Geração do gráfico
            if insight["tipo"] == "grafico_barras":
                chart = alt.Chart(df).mark_bar().encode(
                    x=insight["eixo_x"],
                    y=insight["eixo_y"]
                )
            elif insight["tipo"] == "grafico_linha":
                chart = alt.Chart(df).mark_line(point=True).encode(
                    x=insight["eixo_x"],
                    y=insight["eixo_y"]
                )
            elif insight["tipo"] == "grafico_pizza":
                chart = alt.Chart(df).mark_arc().encode(
                    theta=insight["eixo_y"],
                    color=insight["eixo_x"]
                )

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Erro ao gerar gráfico: {e}")


    # Valor total (se existir)
    if insight.get("valor_total") is not None:
        st.metric("Valor Total", f"R$ {insight['valor_total']:,.2f}")
