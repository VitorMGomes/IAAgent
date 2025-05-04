import json
import os
import pandas as pd

import requests
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/Dados.csv")

"""
docs: https://platform.openai.com/docs/guides/function-calling
"""

# --------------------------------------------------------------
# Define the tool (function) that we want to call
# --------------------------------------------------------------


def get_SalarioBaseMedia():
    """Essa é uma função que retorna a média do salario base dentro do periodo total que o colaborador esteve na empresa"""
    media = round(df["Salário Base"].mean(), 2)
    print(media)
    return {"media_salario_base": media}


# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
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
    }
]

system_prompt = "Voce responde questoes sobre a folha de pagamento."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Qual a média total do salário base do colaborador?"},
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
# Step 3: Execute get_weather function
# --------------------------------------------------------------


def call_function(name, args):
    if name == "get_SalarioBaseMedia":
        return get_SalarioBaseMedia()

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


class SalarioBaseMediaResponse(BaseModel):
    media_salario_base: float = Field(
        description="A média dos salários base em reais."
    )
    response: str = Field(
        description="Uma resposta em linguagem natural explicando o valor médio de salário base."
    )

completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    response_format=SalarioBaseMediaResponse,
)

# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed
print(final_response.media_salario_base)
print(final_response.response)