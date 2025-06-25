import streamlit as st
import requests

st.set_page_config(page_title="Chat Bot", page_icon="🤖")
st.title("🤖 Chat Bot")
st.write("Converse com o agente. Os insights visuais aparecerão na aba 'Insights Personalizados'.")

# Prompt inicial fixo
system_prompt = {
    "role": "system",
    "content": "Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual."
}

# Inicializa sessões
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]
if "insights" not in st.session_state:
    st.session_state.insights = []

# Entrada do usuário
pergunta = st.chat_input("Digite sua pergunta")

if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})

    with st.spinner("Consultando o agente..."):
        try:
            resposta_api = requests.post(
                "http://127.0.0.1:8000/pergunta",  # ✅ Corrigido para o modelo da API
                json={"user_message": pergunta}
            )
            resposta_json = resposta_api.json()
            resposta = resposta_json.get("resposta", "⚠️ Erro: resposta ausente.")
            insight = resposta_json.get("insight")
        except Exception as e:
            resposta = f"❌ Erro ao consultar a API: {str(e)}"
            insight = None

    st.session_state.messages.append({"role": "assistant", "content": resposta})

    if insight and isinstance(insight, dict):
        st.session_state.insights.append(insight)

# Estilos de exibição
st.markdown("""
    <style>
    .msg {
        padding: 0.8em 1.2em;
        margin: 0.5em 0;
        border-radius: 15px;
        font-size: 16px;
        line-height: 1.5;
        max-width: 80%;
    }
    .user-msg { text-align: right; background-color: #3c3c3c; color: white; margin-left: auto; }
    .assistant-msg { text-align: left; background-color: #222; color: white; margin-right: auto; }
    </style>
""", unsafe_allow_html=True)

# Renderiza o histórico do chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user-msg">👤 {msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="msg assistant-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
