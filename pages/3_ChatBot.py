import streamlit as st
import requests

st.set_page_config(page_title="Chat Bot", page_icon="🤖")
st.title("Chat Bot")
st.write("Interaja com o chatbot aqui.")

# Prompt inicial do sistema
system_prompt = {
    "role": "system",
    "content": "Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual."
}

# Inicializa o histórico com o system prompt se ainda não existir
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]

# Campo de entrada do usuário
pergunta = st.chat_input("Digite sua pergunta")

if pergunta:
    # Adiciona pergunta do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": pergunta})

    # Envia o histórico completo para a API
    try:
        resposta_api = requests.post(
            "http://localhost:8000/pergunta",  # Altere se necessário
            json={"messages": st.session_state.messages}
        )
        resposta_json = resposta_api.json()
        resposta = resposta_json.get("resposta", f"⚠️ Erro na resposta: {resposta_json}")
    except Exception as e:
        resposta = f"❌ Erro ao consultar a API: {str(e)}"

    # Adiciona resposta do modelo ao histórico
    st.session_state.messages.append({"role": "assistant", "content": resposta})

# Estilos customizados
st.markdown("""
    <style>
    .user-msg {
        text-align: right;
        background-color: #2c2c2c;
        padding: 0.75em 1em;
        border-radius: 10px;
        margin: 0.5em 0;
        color: white;
        margin-left: 20%;
    }
    .assistant-msg {
        text-align: left;
        background-color: #1a1a1a;
        padding: 0.75em 1em;
        border-radius: 10px;
        margin: 0.5em 0;
        color: white;
        margin-right: 20%;
    }
    </style>
""", unsafe_allow_html=True)

# Exibe todas as mensagens (exceto o system prompt)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="assistant-msg">{msg["content"]}</div>', unsafe_allow_html=True)
