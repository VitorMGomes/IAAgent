# chatbot.py
import streamlit as st
import requests

st.set_page_config(page_title="Slip-Pay Agent", page_icon="🤖", layout="wide")
st.title("🤖 Chat Bot")
st.write("Converse com o agente. Qualquer insight retornado ficará salvo para a página “Insights Personalizados”.")

# ---------- sessão ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "insights" not in st.session_state:
    st.session_state.insights = []

# ---------- entrada ----------
pergunta = st.chat_input("Digite sua pergunta")
if pergunta:
    # exibe imediatamente a pergunta no histórico local
    st.session_state.messages.append({"role": "user", "content": pergunta})

    with st.spinner("Consultando agente..."):
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/chat",          # ← rota correta
                json={"mensagem": pergunta}             # ← chave esperada pela API
            )
            resp.raise_for_status()
            body = resp.json()
            resposta_texto = body.get("resposta", "⚠️ Sem resposta.")
            insights = body.get("insights", [])
        except Exception as e:
            resposta_texto = f"❌ Erro ao chamar API: {e}"
            insights = []

    # ---------- armazena retorno ----------
    st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
    # acumula todos os insights retornados
    if isinstance(insights, list):
        st.session_state.insights.extend(insights)

# ---------- exibe histórico ----------
st.markdown(
    """
    <style>
      .msg {padding:0.8em 1.2em;margin:0.5em 0;border-radius:15px;max-width:80%;}
      .user-msg{background:#3c3c3c;color:white;text-align:right;margin-left:auto;}
      .assistant-msg{background:#222;color:white;text-align:left;margin-right:auto;}
    </style>
    """,
    unsafe_allow_html=True,
)

for m in st.session_state.messages:
    cls = "user-msg" if m["role"] == "user" else "assistant-msg"
    icon = "👤" if m["role"] == "user" else "🤖"
    st.markdown(f'<div class="msg {cls}">{icon} {m["content"]}</div>', unsafe_allow_html=True)
