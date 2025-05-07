import json
import os
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/Dados.csv")

# --------------------------------------------------------------
# Defining the functions we want to call
# --------------------------------------------------------------


def get_SalarioBaseMedia():
    """Essa é uma função que retorna a média do salario base dentro do periodo total que o colaborador esteve na empresa"""
    media = round(df["Salário Base"].mean(), 2)
    return {"media_salario_base": media}

def get_informacoesCabecalho():
    """Essa função retorna quais informações estão presentes na folha de pagamento (coluna do CSV), como descontos legais e beneficios concedidos"""
    cabecalho = df.columns.tolist()
    return {"informações_presentes": cabecalho}

def get_Maior(coluna: str) -> dict:
    """Essa função envia a maior ['coluna'] do colaborador dentro de todo seu periodo na empresa"""
    maior = float(df[coluna].max())
    return {"maior_comissao": maior}

def get_total(coluna: str) -> dict:
    """Retorna o total (soma) dos valores da coluna especificada para o colaborador filtrado."""
    total = int(round(df[coluna].sum(), 2))
    return {f"total_{coluna}": total}

def get_evolucao(coluna: str) -> dict:
    """Retorna a evolução mês a mês dos valores da coluna especificada para o colaborador filtrado."""
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    historico = list(zip(
        dados_ordenados["Mês"] + "-" + dados_ordenados["Ano"].astype(str),
        dados_ordenados[coluna]
    ))

    return {f"evolucao_{coluna}": historico}

def get_mes_ano(coluna: str, mes: str, ano: int) -> dict:
    """Retorna o valor de uma coluna para um determinado mês e ano do colaborador filtrado."""
    linha = df[(df["Mês"] == mes) & (df["Ano"] == ano)]
    if linha.empty:
        return {f"{coluna}_{mes}_{ano}": None}

    valor = float(linha[coluna].values[0])
    return {f"{coluna}_{mes}_{ano}": valor}

def get_crescimento_percentual(coluna: str) -> dict:
    """Retorna o crescimento percentual dos valores da coluna do primeiro ao último mês."""
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    if len(dados_ordenados) < 2:
        return {f"crescimento_percentual_{coluna}": 0.0}
    inicial = dados_ordenados[coluna].iloc[0]
    final = dados_ordenados[coluna].iloc[-1]

    if inicial == 0:
        return {f"crescimento_percentual_{coluna}": 0.0}

    crescimento = ((final - inicial) / inicial) * 100
    return {f"crescimento_percentual_{coluna}": round(crescimento, 2)}

def get_crescimento_percentual_periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o crescimento percentual entre dois períodos para a coluna indicada."""
    dados = df.copy()
    dados_inicial = dados[(dados["Mês"] == mes_inicial) & (dados["Ano"] == ano_inicial)]
    dados_final = dados[(dados["Mês"] == mes_final) & (dados["Ano"] == ano_final)]

    if dados_inicial.empty or dados_final.empty:
        return {"erro": "Período inicial ou final não encontrado nos dados."}

    valor_inicial = dados_inicial[coluna].values[0]
    valor_final = dados_final[coluna].values[0]

    if valor_inicial == 0:
        return {f"crescimento_percentual_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": 0.0}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100
    return {
        f"crescimento_percentual_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}":
        round(crescimento, 2)
    }


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
            "name": "get_Maior",
            "description": "Retorna o maior valor da coluna especificada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna a ser avaliada (ex: 'Comissão', 'Total Vencimentos')"
                    }
                },
                "required": ["coluna"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_total",
            "description": "Retorna o total (soma) dos valores da coluna especificada para o colaborador filtrado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna numérica a ser somada (ex: 'Comissão', 'Plano de Saúde')"
                    }
                },
                "required": ["coluna"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_evolucao",
            "description": "Retorna a evolução mês a mês dos valores da coluna especificada para o colaborador filtrado",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna numérica a ser somada (ex: 'Comissão', 'Plano de Saúde')"
                    }
                },
                "required": ["coluna"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    { 
        "type": "function",
        "function": {
            "name": "get_mes_ano",
            "description": "Retorna o valor da coluna especificada em um mês e ano específicos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna (ex: 'Comissão', 'IRRF (R$)', 'Plano de Saúde')"
                    },
                    "mes": {
                        "type": "string",
                        "description": "Nome do mês (ex: 'Janeiro', 'Fevereiro', 'Abril')"
                    },
                    "ano": {
                        "type": "integer",
                        "description": "Ano da consulta (ex: 2023)"
                    }
                },
                "required": ["coluna", "mes", "ano"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crescimento_percentual",
            "description": "Retorna o crescimento percentual da coluna do primeiro ao último mês.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna numérica a ser analisada (ex: 'Salário Base', 'Total Vencimentos')"
                    }
                },
                "required": ["coluna"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crescimento_percentual_periodo",
            "description": "Retorna o crescimento percentual entre dois meses/anos para a coluna especificada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coluna": {
                        "type": "string",
                        "description": "Nome da coluna (ex: 'Líquido a Receber')"
                    },
                    "mes_inicial": {
                        "type": "string",
                        "description": "Mês de início (ex: 'Janeiro')"
                    },
                    "ano_inicial": {
                        "type": "integer",
                        "description": "Ano de início (ex: 2022)"
                    },
                    "mes_final": {
                        "type": "string",
                        "description": "Mês final (ex: 'Dezembro')"
                    },
                    "ano_final": {
                        "type": "integer",
                        "description": "Ano final (ex: 2023)"
                    }
                },
                "required": ["coluna", "mes_inicial", "ano_inicial", "mes_final", "ano_final"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

   
]

cabecalho = df.columns.tolist()
prompt_colunas = f"Essas são as colunas disponíveis na folha de pagamento: {', '.join(cabecalho)}."

system_prompt = (
    "Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual. "
    "Nunca fale sobre dados de outros colaboradores ou sobre valores médios da empresa. "
    "Sempre responda com base apenas nos dados do colaborador atual.\n"
    f"{prompt_colunas}\n"
    "Use as funções disponíveis quando necessário para calcular ou buscar as informações corretamente."
)


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Qual o crescimento percentual das Comissões de Janeiro de 2021 ate Julho de 2021?"},
]

completion = client.chat.completions.create(
    model="gpt-4.1-nano",
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
        return get_Maior(args["coluna"])
    elif name == "get_total":
        return get_total(args["coluna"])
    elif name == "get_Maior":
        return get_evolucao(args["coluna"])
    elif name == "get_mes_ano":
        return get_mes_ano(args["coluna"], args["mes"], args["ano"])
    elif name == "get_crescimento_percentual":
        return get_crescimento_percentual(args["coluna"])
    elif name == "get_crescimento_percentual_periodo":
        return get_crescimento_percentual_periodo(
            args["coluna"],
            args["mes_inicial"],
            args["ano_inicial"],
            args["mes_final"],
            args["ano_final"]
        )


for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )


# --------------------------------------------------------------
# Step 4: Generic response with pydantic
# --------------------------------------------------------------

class RespostaGenerica(BaseModel):
    response: str = Field(description="Uma resposta em linguagem natural explicando o resultado da função.")


completion_2 = client.beta.chat.completions.parse(
    model="gpt-4.1-nano",
    messages=messages,
    tools=tools,
    tool_choice="none",  # ← força o modelo a não chamar nenhuma função agora
    response_format=RespostaGenerica,
)
# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed

if final_response is not None:
    print("Resposta final do agente:\n", final_response.response)
else:
    print("O modelo não retornou uma resposta compatível com o schema esperado (RespostaGenerica).")
    print("Conteúdo bruto retornado:")
    print(completion_2.choices[0].message.model_dump_json(indent=2))
    
    
    
    
    
# print("\n--- Tokens usados na primeira chamada ---")
# print(f"Prompt tokens: {completion.usage.prompt_tokens}")
# print(f"Completion tokens: {completion.usage.completion_tokens}")
# print(f"Total tokens: {completion.usage.total_tokens}")

# print("\n--- Tokens usados na segunda chamada (resposta final) ---")
# print(f"Prompt tokens: {completion_2.usage.prompt_tokens}")
# print(f"Completion tokens: {completion_2.usage.completion_tokens}")
# print(f"Total tokens: {completion_2.usage.total_tokens}")