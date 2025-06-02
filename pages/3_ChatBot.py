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

# Exibe todas as mensagens (ignora o system prompt na visualização)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
