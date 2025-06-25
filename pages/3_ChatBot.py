import streamlit as st
import requests

st.set_page_config(page_title="Chat Bot", page_icon="🤖")
st.title("🤖 Chat Bot")
st.write("Interaja com o chatbot aqui.")

system_prompt = {
    "role": "system",
    "content": "Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual."
}

if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]

if "insights" not in st.session_state:
    st.session_state.insights = []

pergunta = st.chat_input("Digite sua pergunta")

if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})
    try:
        resposta_api = requests.post(
            "http://localhost:8000/pergunta",
            json={"messages": st.session_state.messages}
        )
        resposta_json = resposta_api.json()
        resposta = resposta_json.get("resposta", f"⚠️ Erro na resposta: {resposta_json}")
    except Exception as e:
        resposta = f"❌ Erro ao consultar a API: {str(e)}"

    # Adiciona a resposta ao chat
    st.session_state.messages.append({"role": "assistant", "content": resposta})

    # Salva insight, se aplicável
    def processar_insight(pergunta, resposta):
        if isinstance(resposta, dict) and "tipo" in resposta:
            st.session_state.insights.append({
                "pergunta": pergunta,
                "tipo": resposta["tipo"],
                "conteudo": resposta
            })
        elif isinstance(resposta, str):
            st.session_state.insights.append({
                "pergunta": pergunta,
                "tipo": "texto",
                "conteudo": resposta
            })

    processar_insight(pergunta, resposta)

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
    .user-msg {
        text-align: right;
        background-color: #3c3c3c;
        color: white;
        margin-left: auto;
        margin-right: 0;
    }
    .assistant-msg {
        text-align: left;
        background-color: #222;
        color: white;
        margin-right: auto;
        margin-left: 0;
    }
    </style>
""", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user-msg">👤 {msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="msg assistant-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
