import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
    model="gpt-4.1-nano-2025-04-14",
    messages=[
        {"role" : "system", "content": "Você é um assistente que responde sobre folhas de pagamento."},
        {
            "role": "user",
            "content" : "Me fale como é calculado o desconto do FGTS na folha de pagamento"
        }
    ]
)

response = completion.choices[0].message.content
print(response)
