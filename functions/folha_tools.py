import os
import pandas as pd
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

df = pd.read_csv("data/Dados.csv")

# Mapeia os meses para números logo após carregar o DataFrame
mes_map = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}
df["Mês"] = df["Mês"].map(mes_map)

retriever = Chroma(
    persist_directory="./chrome_langchain_db",
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
).as_retriever()

rag_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    retriever=retriever,
    return_source_documents=False
)


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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena os dados para facilitar o filtro por período
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) | 
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) | 
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena os dados por ano e mês para facilitar o filtro
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    
    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) | 
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) | 
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # Cria lista com (Mês-Ano, valor da coluna)
    historico = list(zip(
        periodo["Mês"].astype(str) + "-" + periodo["Ano"].astype(str),
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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Filtra os dados para o mês/ano inicial e final
    dados_inicial = df[(df["Mês"] == mes_inicial_num) & (df["Ano"] == ano_inicial)]
    dados_final = df[(df["Mês"] == mes_final_num) & (df["Ano"] == ano_final)]

    if dados_inicial.empty or dados_final.empty:
        return {"erro": "Período inicial ou final não encontrado nos dados."}

    valor_inicial = dados_inicial[coluna].values[0]
    valor_final = dados_final[coluna].values[0]

    if valor_inicial == 0:
        return {
            f"crescimento_percentual_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": 0.0
        }

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

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena e filtra o DataFrame no intervalo especificado
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    total = sum(periodo[coluna].sum() for coluna in colunas_desconto)
    return {
        f"total_descontos_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": round(total, 2)
    }

def get_Menor(coluna: str) -> dict:
    """Retorna o menor valor da coluna especificada, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    idx_menor = df[coluna].idxmin()
    linha_menor = df.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = linha_menor["Mês"]
    ano = linha_menor["Ano"]

    return {
        f"menor_{coluna}": valor,
        "mes": mes,
        "ano": ano
    }

def get_Menor_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o menor valor da coluna especificada dentro de um período, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Mapeamento dos meses para números
    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    # Ordena os dados por ano e mês para facilitar o filtro
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    
    # Filtra o período desejado
    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) | 
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) | 
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    idx_menor = periodo[coluna].idxmin()
    linha_menor = periodo.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = linha_menor["Mês"]
    ano = linha_menor["Ano"]

    return {
        f"menor_{coluna}_{mes_inicial}_{ano_inicial}_ate_{mes_final}_{ano_final}": valor,
        "mes": mes,
        "ano": ano
    }

def get_menor_ultimo(coluna: str, meses: int) -> dict:
    """Retorna o menor valor da coluna nos últimos N meses, juntamente com seu mês e ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Ordena os dados por ano e mês
    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    # Seleciona os últimos N meses
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    idx_menor = ultimos_dados[coluna].idxmin()
    linha_menor = ultimos_dados.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = linha_menor["Mês"]
    ano = linha_menor["Ano"]

    return {
        f"menor_{coluna}_ultimos_{meses}_meses": valor,
        "mes": mes,
        "ano": ano
    }
