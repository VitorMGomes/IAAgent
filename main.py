import json
import os
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/Dados.csv")

# --------------------------------------------------------------
# Base Vetorial para RAG
# --------------------------------------------------------------
retriever = Chroma(
    persist_directory="./chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
).as_retriever()

rag_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    retriever=retriever,
    return_source_documents=False
)

# --------------------------------------------------------------
# Funções com base em CSV e RAG
# --------------------------------------------------------------

def consultar_documento_txt_ou_pdf(pergunta: str) -> dict:
    resposta = rag_chain.run(pergunta)
    return {"resposta": resposta}

def get_informacoesCabecalho() -> dict:
    """Retorna o cabeçalho com os nomes das colunas presentes no CSV da folha de pagamento."""
    cabecalho = df.columns.tolist()
    return {"informacoes_presentes": cabecalho}

def get_Media(coluna: str) -> dict:
    """Retorna a média de todos os valores da coluna especificada."""
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}
    media = round(df[coluna].mean(), 2)
    return {f"media_{coluna}": media}

def get_Media_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a média dos valores da coluna especificada dentro de um período entre mes/ano e mes/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados para facilitar o filtro por período
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) | 
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) | 
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    media = round(periodo[coluna].mean(), 2)
    return {
        f"media_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": media
    }

def get_Media_Ultimo(coluna: str, meses: int) -> dict:
    """Retorna a média da coluna solicitada considerando os últimos N meses."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena por ano e mês para garantir que os últimos meses fiquem no final
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    
    # Seleciona os últimos N meses
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para calcular a média dos últimos meses."}

    media = round(ultimos_dados[coluna].mean(), 2)
    return {
        f"media_{coluna}_ultimos_{meses}_meses": media
    }

def get_Maior(coluna: str) -> dict:
    """Retorna o maior valor da coluna especificada, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    idx_maior = df[coluna].idxmax()
    linha_maior = df.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = linha_maior["Mês"]
    ano = linha_maior["Ano"]

    return {
        f"maior_{coluna}": valor,
        "mes": mes,
        "ano": ano
    }

def get_Maior_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o maior valor da coluna especificada dentro de um período, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados por ano e mês para facilitar o filtro
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    
    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) | 
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) | 
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    idx_maior = periodo[coluna].idxmax()
    linha_maior = periodo.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = linha_maior["Mês"]
    ano = linha_maior["Ano"]

    return {
        f"maior_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": valor,
        "mes": mes,
        "ano": ano
    }

def get_maior_ultimo(coluna: str, meses: int) -> dict:
    """Retorna o maior valor da coluna nos últimos N meses, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Seleciona os últimos N meses
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    idx_maior = ultimos_dados[coluna].idxmax()
    linha_maior = ultimos_dados.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = linha_maior["Mês"]
    ano = linha_maior["Ano"]

    return {
        f"maior_{coluna}_ultimos_{meses}_meses": valor,
        "mes": mes,
        "ano": ano
    }

def get_total(coluna: str) -> dict:
    """Retorna a soma de todos os valores da coluna especificada."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    total = round(df[coluna].sum(), 2)
    return {f"total_{coluna}": total}

def get_total_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a soma dos valores da coluna especificada dentro de um período entre mes/ano e mes/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    total = round(periodo[coluna].sum(), 2)
    return {
        f"total_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": total
    }

def get_total_ultimo(coluna: str, meses: int) -> dict:
    """Retorna a soma dos valores da coluna especificada nos últimos N meses."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados cronologicamente
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Seleciona os últimos N meses
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    total = round(ultimos_dados[coluna].sum(), 2)
    return {
        f"total_{coluna}_ultimos_{meses}_meses": total
    }

def get_evolucao(coluna: str) -> dict:
    """Retorna a evolução mês a mês da coluna especificada durante todo o período."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados cronologicamente
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Cria uma lista com (Mês-Ano, valor da coluna)
    historico = list(zip(
        dados_ordenados["Mês"] + "-" + dados_ordenados["Ano"].astype(str),
        dados_ordenados[coluna].round(2)
    ))

    return {f"evolucao_{coluna}": historico}

def get_evolucao_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a evolução mês a mês da coluna especificada dentro de um período entre mes/ano e mes/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # Cria lista com (Mês-Ano, valor da coluna)
    historico = list(zip(
        periodo["Mês"] + "-" + periodo["Ano"].astype(str),
        periodo[coluna].round(2)
    ))

    return {
        f"evolucao_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": historico
    }

def get_mes_ano(coluna: str, mes: str, ano: int) -> dict:
    """Retorna o valor da coluna especificada em um mês e ano determinados."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    linha = df[(df["Mês"] == mes) & (df["Ano"] == ano)]

    if linha.empty:
        return {"erro": f"Não há dados para {mes}/{ano}."}

    valor = round(float(linha[coluna].values[0]), 2)
    return {f"{coluna}_{mes}_{ano}": valor}

def get_crescimento_percentual(coluna: str) -> dict:
    """Retorna o crescimento percentual da coluna do primeiro até o último mês."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados cronologicamente
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    if len(dados_ordenados) < 2:
        return {"erro": "Não há dados suficientes para calcular crescimento percentual."}

    valor_inicial = dados_ordenados[coluna].iloc[0]
    valor_final = dados_ordenados[coluna].iloc[-1]

    if valor_inicial == 0:
        return {f"crescimento_percentual_{coluna}": 0.0}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100
    return {f"crescimento_percentual_{coluna}": round(crescimento, 2)}

def get_crescimento_percentual_periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o crescimento percentual da coluna dentro de um período entre mes/ano e mes/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Filtra os dados para o mês/ano inicial e final
    dados_inicial = df[(df["Mês"] == mes_inicial) & (df["Ano"] == ano_inicial)]
    dados_final = df[(df["Mês"] == mes_final) & (df["Ano"] == ano_final)]

    if dados_inicial.empty or dados_final.empty:
        return {"erro": "Período inicial ou final não encontrado nos dados."}

    valor_inicial = dados_inicial[coluna].values[0]
    valor_final = dados_final[coluna].values[0]

    if valor_inicial == 0:
        return {f"crescimento_percentual_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": 0.0}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100
    return {
        f"crescimento_percentual_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": round(crescimento, 2)
    }

def get_total_descontos() -> dict:
    """Retorna a soma total de todos os descontos em todo o período."""

    colunas_desconto = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]

    for coluna in colunas_desconto:
        if coluna not in df.columns:
            return {"erro": f"A coluna de desconto '{coluna}' não foi encontrada na base de dados."}

    total = sum(df[coluna].sum() for coluna in colunas_desconto)
    return {"total_descontos": round(total, 2)}

def get_total_descontos_Periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a soma total de todos os descontos dentro de um período entre mes/ano e mes/ano."""

    colunas_desconto = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]

    for coluna in colunas_desconto:
        if coluna not in df.columns:
            return {"erro": f"A coluna de desconto '{coluna}' não foi encontrada na base de dados."}

    # Ordena e filtra o DataFrame no intervalo especificado
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    total = sum(periodo[coluna].sum() for coluna in colunas_desconto)
    return {
        f"total_descontos_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": round(total, 2)
    }

def get_liquido_total() -> dict:
    """Retorna o total líquido recebido em todo o período."""

    coluna_liquido = "Líquido a Receber"

    if coluna_liquido not in df.columns:
        return {"erro": f"A coluna '{coluna_liquido}' não foi encontrada na base de dados."}

    total = round(df[coluna_liquido].sum(), 2)
    return {"total_liquido_recebido": total}

def get_liquido_periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o total líquido recebido dentro de um período entre mes/ano e mes/ano."""

    coluna_liquido = "Líquido a Receber"

    if coluna_liquido not in df.columns:
        return {"erro": f"A coluna '{coluna_liquido}' não foi encontrada na base de dados."}

    # Ordena os dados cronologicamente
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Filtra o período especificado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    total = round(periodo[coluna_liquido].sum(), 2)
    return {
        f"liquido_recebido_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": total
    }

def get_liquido_percentual() -> dict:
    """Retorna o crescimento percentual do valor líquido recebido durante todo o período."""

    coluna_liquido = "Líquido a Receber"

    if coluna_liquido not in df.columns:
        return {"erro": f"A coluna '{coluna_liquido}' não foi encontrada na base de dados."}

    # Ordena os dados cronologicamente
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    if len(dados_ordenados) < 2:
        return {"erro": "Não há dados suficientes para calcular o crescimento percentual."}

    valor_inicial = dados_ordenados[coluna_liquido].iloc[0]
    valor_final = dados_ordenados[coluna_liquido].iloc[-1]

    if valor_inicial == 0:
        return {"crescimento_percentual_liquido": 0.0}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100
    return {"crescimento_percentual_liquido": round(crescimento, 2)}

def get_liquido_percentual_periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o crescimento percentual do valor líquido recebido dentro de um período entre mes/ano e mes/ano."""

    coluna_liquido = "Líquido a Receber"

    if coluna_liquido not in df.columns:
        return {"erro": f"A coluna '{coluna_liquido}' não foi encontrada na base de dados."}

    # Filtra os dados para o mês/ano inicial e final
    dados_inicial = df[(df["Mês"] == mes_inicial) & (df["Ano"] == ano_inicial)]
    dados_final = df[(df["Mês"] == mes_final) & (df["Ano"] == ano_final)]

    if dados_inicial.empty or dados_final.empty:
        return {"erro": "Período inicial ou final não encontrado nos dados."}

    valor_inicial = dados_inicial[coluna_liquido].values[0]
    valor_final = dados_final[coluna_liquido].values[0]

    if valor_inicial == 0:
        return {
            f"crescimento_percentual_liquido_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": 0.0
        }

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100
    return {
        f"crescimento_percentual_liquido_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": round(crescimento, 2)
    }


# --------------------------------------------------------------
# Step 1: Call model with the funcion tool define
# --------------------------------------------------------------

tools = [
  {
    "type": "function",
    "function": {
      "name": "consultar_documento_txt_ou_pdf",
      "description": "Consulta os documentos (PDF ou TXT) indexados para responder perguntas não-numéricas sobre a folha.",
      "parameters": {
        "type": "object",
        "properties": {
          "pergunta": {
            "type": "string",
            "description": "Pergunta sobre os documentos, como 'O que é FGTS?' ou 'Como funciona o IRRF?'."
          }
        },
        "required": [
          "pergunta"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
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
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_Media",
      "description": "Retorna a média de todos os valores da coluna especificada.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna a ser analisada (ex: 'Comissão', 'Plano de Saúde')."
          }
        },
        "required": [
          "coluna"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_Media_Periodo",
      "description": "Retorna a média da coluna especificada dentro de um período mes/ano - mes/ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial (ex: 'Janeiro')"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial (ex: 2022)"
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
        "required": [
          "coluna",
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_Media_Ultimo",
      "description": "Retorna a média da coluna nos últimos N meses.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "meses": {
            "type": "integer",
            "description": "Quantidade de meses a considerar a partir do fim."
          }
        },
        "required": [
          "coluna",
          "meses"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_Maior",
      "description": "Retorna o maior valor da coluna especificada junto com mês e ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          }
        },
        "required": [
          "coluna"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_Maior_Periodo",
      "description": "Retorna o maior valor da coluna especificada dentro de um período, com mês e ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "coluna",
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_maior_ultimo",
      "description": "Retorna o maior valor da coluna nos últimos N meses, com mês e ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "meses": {
            "type": "integer",
            "description": "Quantidade de meses a considerar."
          }
        },
        "required": [
          "coluna",
          "meses"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_total",
      "description": "Retorna o total (soma) dos valores da coluna especificada.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          }
        },
        "required": [
          "coluna"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_total_Periodo",
      "description": "Retorna o total da coluna dentro de um período mes/ano - mes/ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "coluna",
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_total_ultimo",
      "description": "Retorna o total da coluna nos últimos N meses.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "meses": {
            "type": "integer",
            "description": "Quantidade de meses."
          }
        },
        "required": [
          "coluna",
          "meses"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_evolucao",
      "description": "Retorna a evolução mês a mês dos valores da coluna.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          }
        },
        "required": [
          "coluna"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_evolucao_Periodo",
      "description": "Retorna a evolução mês a mês da coluna dentro de um período mes/ano - mes/ano.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "coluna",
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_mes_ano",
      "description": "Retorna o valor da coluna em um mês e ano específicos.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes": {
            "type": "string",
            "description": "Mês (ex: 'Março')"
          },
          "ano": {
            "type": "integer",
            "description": "Ano (ex: 2023)"
          }
        },
        "required": [
          "coluna",
          "mes",
          "ano"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_crescimento_percentual",
      "description": "Retorna o crescimento percentual da coluna entre o primeiro e o último mês.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          }
        },
        "required": [
          "coluna"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_crescimento_percentual_periodo",
      "description": "Retorna o crescimento percentual da coluna em um período específico.",
      "parameters": {
        "type": "object",
        "properties": {
          "coluna": {
            "type": "string",
            "description": "Nome da coluna."
          },
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "coluna",
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_total_descontos",
      "description": "Retorna a soma total de todos os descontos em todo o período.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_total_descontos_Periodo",
      "description": "Retorna a soma total de todos os descontos dentro de um período.",
      "parameters": {
        "type": "object",
        "properties": {
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_liquido_total",
      "description": "Retorna o total líquido recebido em todo o período.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_liquido_periodo",
      "description": "Retorna o total líquido recebido dentro de um período.",
      "parameters": {
        "type": "object",
        "properties": {
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_liquido_percentual",
      "description": "Retorna o crescimento percentual do líquido recebido durante todo o período.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      },
      "strict": true
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_liquido_percentual_periodo",
      "description": "Retorna o crescimento percentual do líquido em um período.",
      "parameters": {
        "type": "object",
        "properties": {
          "mes_inicial": {
            "type": "string",
            "description": "Mês inicial"
          },
          "ano_inicial": {
            "type": "integer",
            "description": "Ano inicial"
          },
          "mes_final": {
            "type": "string",
            "description": "Mês final"
          },
          "ano_final": {
            "type": "integer",
            "description": "Ano final"
          }
        },
        "required": [
          "mes_inicial",
          "ano_inicial",
          "mes_final",
          "ano_final"
        ],
        "additionalProperties": false
      },
      "strict": true
    }
  }
]


retriever = Chroma(
    persist_directory="./chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
).as_retriever()


cabecalho = df.columns.tolist()
prompt_colunas = f"Essas são as colunas disponíveis na folha de pagamento: {', '.join(cabecalho)}."

system_prompt = (
    "Você é um agente inteligente que responde dúvidas sobre a folha de pagamento de um colaborador individual. "
    "Nunca fale sobre dados de outros colaboradores ou sobre valores médios da empresa. "
    "Sempre responda com base apenas nos dados do colaborador atual.\n"
    f"{prompt_colunas}\n"
    "Use as funções disponíveis quando necessário para calcular ou buscar as informações corretamente. "
    "Você pode consultar documentos PDF e textos técnicos (como explicações sobre FGTS, PIS, IRRF, CBO etc) que foram carregados na base vetorial. "
    "Se os documentos não forem suficientes, você pode complementar a resposta com seu conhecimento prévio confiável sobre leis trabalhistas, benefícios e temas relacionados à folha de pagamento no Brasil. "
    "Evite mencionar valores fixos de impostos, percentuais ou faixas salariais que possam ter mudado, a menos que estejam presentes nos documentos carregados. "
    "Ao chamar funções, use exatamente os nomes das colunas listadas acima para garantir que a análise seja correta."
)



messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "O que é o PIS?"},
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
    elif name == "consultar_documento_txt_ou_pdf":
        return consultar_documento_txt_ou_pdf(args["pergunta"])


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

messages.append({
    "role": "user",
    "content": (
        "Revise a resposta anterior. Corrija erros de português, melhore a fluidez e complete com base em seu conhecimento "
        "caso a explicação esteja incompleta, pouco clara ou superficial."
    )
})

class RespostaFinalMelhorada(BaseModel):
    response: str = Field(description="Uma resposta clara, corrigida e completa sobre o assunto.")

completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    response_format=RespostaFinalMelhorada
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