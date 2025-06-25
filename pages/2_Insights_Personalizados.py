import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Insights Personalizados", page_icon="📈")
st.title("📊 Insights Personalizados")
st.write("Aqui você verá os gráficos e análises gerados automaticamente enquanto conversa com o agente.")

# Se não houver insights
if "insights" not in st.session_state or not st.session_state.insights:
    st.info("Nenhum insight foi gerado ainda. Volte ao chatbot e faça uma pergunta.")
    st.stop()

# Itera por cada insight acumulado
for idx, insight in enumerate(st.session_state.insights, start=1):
    st.markdown(f"### {idx}. {insight.get('titulo', '')}")

    # JSON bruto para depuração
    with st.expander("🔍 Ver dados brutos do insight", expanded=False):
        st.json(insight)

    tipo = insight.get("tipo")
    raw_data = insight.get("dados") or []
    eixo_x = insight.get("eixo_x", "x")
    eixo_y = insight.get("eixo_y", "y")
    records = []

    # Parseamento flexível de dados
    if isinstance(raw_data, list):
        for item in raw_data:
            if isinstance(item, dict):
                # Caso o dict já contenha as chaves de eixo_x e eixo_y
                if eixo_x in item and eixo_y in item:
                    x_val = item.get(eixo_x)
                    y_val = item.get(eixo_y)
                    records.append({eixo_x: x_val, eixo_y: y_val})
                else:
                    # Caso seja dict {x_val: y_val}
                    for x_val, y_val in item.items():
                        records.append({eixo_x: x_val, eixo_y: y_val})
    else:
        st.warning("Formato de dados inesperado (esperado lista), não será possível gerar o gráfico.")

    # Se não há registros, avisa e segue
    if not records:
        st.warning("Dados insuficientes para gerar o gráfico.")
        st.markdown("---")
        continue

    # Cria DataFrame
    df_plot = pd.DataFrame(records)

    # Determina ordem de categorias para eixo_x, se nominal
    categories = []
    if eixo_x in df_plot.columns:
        seen = set()
        for v in df_plot[eixo_x].tolist():
            if v not in seen:
                seen.add(v)
                categories.append(v)

    with st.expander("📋 Tabela de dados utilizada", expanded=False):
        st.dataframe(df_plot)

    # Configuração de scale/ordenamento para o eixo X
    sort_param = categories if categories else None
    x_encoding = alt.X(eixo_x, type='nominal', sort=sort_param)
    y_encoding = alt.Y(eixo_y)

    # Geração do gráfico
    if tipo == "grafico_barras":
        chart = (
            alt.Chart(df_plot)
               .mark_bar()
               .encode(
                   x=x_encoding,
                   y=y_encoding
               )
               .properties(title=insight.get('titulo', ''))
        )
    elif tipo == "grafico_linha":
        chart = (
            alt.Chart(df_plot)
               .mark_line(point=True)
               .encode(
                   x=x_encoding,
                   y=y_encoding
               )
               .properties(title=insight.get('titulo', ''))
        )
    elif tipo == "grafico_pizza":
        chart = (
            alt.Chart(df_plot)
               .mark_arc()
               .encode(
                   theta=alt.Theta(eixo_y),
                   color=alt.Color(eixo_x)
               )
               .properties(title=insight.get('titulo', ''))
        )
    else:
        st.warning(f"Tipo de insight não suportado: {tipo}")
        st.markdown("---")
        continue

    st.altair_chart(chart, use_container_width=True)

    # Métrica de valor total, se existir
    if insight.get("valor_total") is not None:
        try:
            total = float(insight.get("valor_total"))
            st.metric("Valor Total", f"R$ {total:,.2f}")
        except Exception:
            st.metric("Valor Total", str(insight.get("valor_total")))

    st.markdown("---")
