
import pandas as pd
from auth.login import autenticar_usuario
from utils.preprocessor import processar_dados
from workflow.agent import responder

def executar():
    print("📥 Carregando dados da folha de pagamento...")
    df = pd.read_csv("data/holerite.csv", sep=";")

    print("🧼 Pré-processando dados...")
    df = processar_dados(df)

    # Login por e-mail
    email = input("🔐 Digite seu e-mail para acessar seus dados: ").strip().lower()
    df["Email"] = df["Email"].astype(str).str.strip().str.lower()

    if not autenticar_usuario(email, df):
        print("❌ E-mail não encontrado. Tente novamente.")
        return

    df_usuario = df[df["Email"] == email].copy()
    print("✅ Login realizado com sucesso!")

    # Loop de interação com o agente
    print("\n🤖 Olá! Pode me perguntar sobre sua folha de pagamento.")
    print("📝 Exemplo: 'Qual foi meu salário bruto em fevereiro de 2023?'\n")

    while True:
        pergunta = input("📨 Sua pergunta (ou 'sair'): ").strip()
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("👋 Até mais!")
            break

        resposta = responder(pergunta, df_usuario)
        print(resposta)
