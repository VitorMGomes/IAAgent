import os


from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
    model="gpt-4.1-nano-2025-04-14",
    messages=[
        {"role": "system", "content": "Você é um assistente que ajuda sobre folhas de pagamento da empresa"},
        {
            "role": "user",
            "content": "Como sao feitos os descontos de inss em uma folha de pagamento?"
            
        },
    ],
)

response = completion.choices[0].message.content
print(response)