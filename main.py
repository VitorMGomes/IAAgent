import json
import os
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/Dados.csv")

"""
docs: https://platform.openai.com/docs/guides/function-calling
"""

# --------------------------------------------------------------
# Defining the functions we want to call
# --------------------------------------------------------------


def get_SalarioBaseMedia():
    """Essa é uma função que retorna a média do salario base dentro do periodo total que o colaborador esteve na empresa"""
    media = round(df["Salário Base"].mean(), 2)
    print(media)
    return {"media_salario_base": media}

def get_informacoesCabecalho():
    """Essa função retorna quais informações estão presentes na folha de pagamento, como descontos legais e beneficios concedidos"""
    cabecalho = df.columns.tolist()
    print(cabecalho)
    return {"informações_presentes": cabecalho}

def get_MaiorComissao():
    """Essa função envia a maior comissão do colaborador dentro de todo seu periodo na empresa"""
    maior = float(df["Comissão"].max())
    print(maior)
    return {"maior_comissao": maior}

# --------------------------------------------------------------
# Step 1: Call model with the funcion tool define
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_SalarioBaseMedia",
            "description": "retorna a média do salario base dentro do periodo total que o colaborador esteve na empresa.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_informacoesCabecalho",
            "description": "Retorna quais colunas estão presentes na folha de pagamento.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_MaiorComissao",
            "description": "Retorna a maior comissao do colaborador dentro de todo o tempo de empresa.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "Voce responde questões sobre a folha de pagamento."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Qual são os dados presentes da folha de pagamento?"},
]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

# --------------------------------------------------------------
# Step 2: Model decides to call function(s)
# --------------------------------------------------------------

completion.model_dump()

# --------------------------------------------------------------
# Step 3: Execute the function
# --------------------------------------------------------------


def call_function(name, args):
    if name == "get_SalarioBaseMedia":
        return get_SalarioBaseMedia()
    elif name == "get_informacoesCabecalho":
        return get_informacoesCabecalho()
    elif name == "get_MaiorComissao":
        return get_MaiorComissao()


for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )
# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------


# class SalarioBaseMediaResponse(BaseModel):
#     media_salario_base: float = Field(
#         description="A média dos salários base em reais."
#     )
#     response: str = Field(
#         description="Uma resposta em linguagem natural explicando o valor médio de salário base."
#     )

# --------------------------------------------------------------
# Generic response with pydantic
# --------------------------------------------------------------

class RespostaGenerica(BaseModel):
    response: str = Field(description="Uma resposta em linguagem natural explicando o resultado da função.")


completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    response_format=RespostaGenerica,
)

# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed
print(final_response.response)