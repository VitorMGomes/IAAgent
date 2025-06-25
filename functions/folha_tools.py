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
    """Retorna a média da coluna especificada, junto com todos os valores individuais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    valores = df[coluna].dropna().round(2)

    media = round(valores.mean(), 2)

    dados = [
        {str(i + 1): valor} for i, valor in enumerate(valores)
    ]

    return {
        "media": media,
        "dados": dados
    }

def get_Media_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a média dos valores da coluna especificada dentro de um período entre mes/ano e mes/ano,
    junto com os valores mensais individuais para visualização."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    valores_mensais = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            periodo["Mês"].astype(str),
            periodo["Ano"].astype(str),
            periodo[coluna]
        )
    ]

    media = round(sum(list(d.values())[0] for d in valores_mensais) / len(valores_mensais), 2)

    return {
        "media": media,
        "dados": valores_mensais
    }

def get_Media_Ultimo(coluna: str, meses: int) -> dict:
    """Retorna a média da coluna solicitada considerando os últimos N meses,
    junto com os valores mensais individuais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para calcular a média dos últimos meses."}

    valores_mensais = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            ultimos_dados["Mês"].astype(str),
            ultimos_dados["Ano"].astype(str),
            ultimos_dados[coluna]
        )
    ]

    media = round(sum(list(d.values())[0] for d in valores_mensais) / len(valores_mensais), 2)

    return {
        "media": media,
        "dados": valores_mensais
    }

def get_Maior(coluna: str) -> dict:
    """Retorna o maior valor da coluna especificada, seu mês/ano, e os dados completos da coluna."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    idx_maior = df[coluna].idxmax()
    linha_maior = df.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = str(linha_maior["Mês"])
    ano = str(linha_maior["Ano"])

    dados = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            df["Mês"].astype(str),
            df["Ano"].astype(str),
            df[coluna]
        )
    ]

    return {
        "maior_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": dados
    }

def get_Maior_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o maior valor da coluna especificada dentro de um período, junto com seu mês/ano e os valores do período."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    idx_maior = periodo[coluna].idxmax()
    linha_maior = periodo.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = str(linha_maior["Mês"])
    ano = str(linha_maior["Ano"])

    valores_mensais = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            periodo["Mês"].astype(str),
            periodo["Ano"].astype(str),
            periodo[coluna]
        )
    ]

    return {
        "maior_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": valores_mensais
    }

def get_Maior_Ultimo(coluna: str, meses: int) -> dict:
    """Retorna o maior valor da coluna nos últimos N meses, com mês/ano e todos os valores individuais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    idx_maior = ultimos_dados[coluna].idxmax()
    linha_maior = ultimos_dados.loc[idx_maior]

    valor = round(linha_maior[coluna], 2)
    mes = str(linha_maior["Mês"])
    ano = str(linha_maior["Ano"])

    dados = [
        {f"{m}/{a}": round(v, 2)}
        for m, a, v in zip(
            ultimos_dados["Mês"].astype(str),
            ultimos_dados["Ano"].astype(str),
            ultimos_dados[coluna]
        )
    ]

    return {
        "maior_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": dados
    }

def get_Total(coluna: str) -> dict:
    """Retorna a soma de todos os valores da coluna especificada e os valores individuais por mês/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    total = round(df[coluna].sum(), 2)

    dados = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            df["Mês"].astype(str),
            df["Ano"].astype(str),
            df[coluna]
        )
    ]

    return {
        "valor_total": total,
        "dados": dados
    }

def get_Total_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna os valores mensais e total acumulado da coluna especificada entre mes/ano e mes/ano."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    valores_mensais = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            periodo["Mês"].astype(str),
            periodo["Ano"].astype(str),
            periodo[coluna]
        )
    ]

    total = round(sum(list(v.values())[0] for v in valores_mensais), 2)

    return {
        "dados": valores_mensais,
        "valor_total": total
    }

def get_Total_Ultimo(coluna: str, meses: int) -> dict:
    """Retorna a soma dos valores da coluna especificada nos últimos N meses, com dados mensais individuais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    valores_mensais = [
        {f"{mes}/{ano}": round(valor, 2)}
        for mes, ano, valor in zip(
            ultimos_dados["Mês"].astype(str),
            ultimos_dados["Ano"].astype(str),
            ultimos_dados[coluna]
        )
    ]

    total = round(sum(list(d.values())[0] for d in valores_mensais), 2)

    return {
        "valor_total": total,
        "dados": valores_mensais
    }

def get_Evolucao(coluna: str) -> dict:
    """Retorna a evolução mês a mês da coluna especificada durante todo o período, formatada para visualização."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    dados = [
        {f"{str(mes)}/{str(ano)}": round(valor, 2)}
        for mes, ano, valor in zip(
            dados_ordenados["Mês"],
            dados_ordenados["Ano"],
            dados_ordenados[coluna]
        )
    ]

    return {
        "dados": dados
    }

def get_Evolucao_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna a evolução mês a mês da coluna especificada dentro de um período."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    dados = [
        {f"{str(m)}/{str(a)}": round(v, 2)}
        for m, a, v in zip(periodo["Mês"], periodo["Ano"], periodo[coluna])
    ]

    return {"dados": dados}

def get_Mes_Ano(coluna: str, mes: str, ano: int) -> dict:
    """Retorna o valor da coluna em um mês e ano específicos."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}

    meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_num = meses.get(mes.capitalize())
    if mes_num is None:
        return {"erro": f"Mês '{mes}' inválido."}

    dados_filtrados = df[(df["Mês"] == mes_num) & (df["Ano"] == ano)]

    if dados_filtrados.empty:
        return {"erro": f"Nenhum dado encontrado para {mes}/{ano}."}

    valor = round(dados_filtrados[coluna].values[0], 2)

    return {
        "mes_ano": f"{mes}/{ano}",
        "valor": valor
    }

def get_Crescimento_Percentual(coluna: str) -> dict:
    """Retorna o crescimento percentual da coluna do primeiro até o último mês."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    if len(dados_ordenados) < 2:
        return {"erro": "Não há dados suficientes para calcular crescimento percentual."}

    valor_inicial = dados_ordenados[coluna].iloc[0]
    valor_final = dados_ordenados[coluna].iloc[-1]

    if valor_inicial == 0:
        return {"crescimento_percentual": None, "erro": "Valor inicial é zero, não é possível calcular a variação percentual."}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100

    return {
        "valor_inicial": round(valor_inicial, 2),
        "valor_final": round(valor_final, 2),
        "crescimento_percentual": round(crescimento, 2)
    }

def get_Crescimento_Percentual_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o crescimento percentual da coluna dentro de um período, junto com os dados mensais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_inicial_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_final_num))
    ]

    if periodo.empty or len(periodo) < 2:
        return {"erro": "Período inválido ou com dados insuficientes para calcular o crescimento."}

    valor_inicial = periodo[coluna].iloc[0]
    valor_final = periodo[coluna].iloc[-1]

    if valor_inicial == 0:
        return {"crescimento_percentual": None, "erro": "Valor inicial é zero, não é possível calcular a variação percentual."}

    crescimento = ((valor_final - valor_inicial) / valor_inicial) * 100

    dados = [
        {f"{str(mes)}/{str(ano)}": round(valor, 2)}
        for mes, ano, valor in zip(periodo["Mês"], periodo["Ano"], periodo[coluna])
    ]

    return {
        "valor_inicial": round(valor_inicial, 2),
        "valor_final": round(valor_final, 2),
        "crescimento_percentual": round(crescimento, 2),
        "dados": dados
    }

def get_Menor(coluna: str) -> dict:
    """Retorna o menor valor da coluna especificada, juntamente com seu mês/ano e todos os dados individuais."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    idx_menor = df[coluna].idxmin()
    linha_menor = df.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = str(linha_menor["Mês"])
    ano = str(linha_menor["Ano"])

    dados = [
        {f"{m}/{a}": round(v, 2)}
        for m, a, v in zip(
            df["Mês"].astype(str),
            df["Ano"].astype(str),
            df[coluna]
        )
    ]

    return {
        "menor_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": dados
    }

def get_Menor_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna o menor valor da coluna especificada dentro de um período, com mês/ano e os dados do período."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    idx_menor = periodo[coluna].idxmin()
    linha_menor = periodo.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = str(linha_menor["Mês"])
    ano = str(linha_menor["Ano"])

    dados = [
        {f"{m}/{a}": round(v, 2)}
        for m, a, v in zip(periodo["Mês"].astype(str), periodo["Ano"].astype(str), periodo[coluna])
    ]

    return {
        "menor_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": dados
    }

def get_Menor_Ultimo(coluna: str, meses: int) -> dict:
    """Retorna o menor valor da coluna nos últimos N meses, com mês/ano e todos os dados individuais do período."""

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])
    ultimos_dados = dados_ordenados.tail(meses)

    if ultimos_dados.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    idx_menor = ultimos_dados[coluna].idxmin()
    linha_menor = ultimos_dados.loc[idx_menor]

    valor = round(linha_menor[coluna], 2)
    mes = str(linha_menor["Mês"])
    ano = str(linha_menor["Ano"])

    dados = [
        {f"{m}/{a}": round(v, 2)}
        for m, a, v in zip(
            ultimos_dados["Mês"].astype(str),
            ultimos_dados["Ano"].astype(str),
            ultimos_dados[coluna]
        )
    ]

    return {
        "menor_valor": valor,
        "mes": mes,
        "ano": ano,
        "dados": dados
    }

def get_Resumo_Descontos_Periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna um resumo detalhado dos descontos por tipo e por mês, dentro de um período especificado."""

    colunas_desconto = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]

    for coluna in colunas_desconto:
        if coluna not in df.columns:
            return {"erro": f"A coluna de desconto '{coluna}' não foi encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    resumo = {
        "total_descontos": round(periodo[colunas_desconto].sum().sum(), 2),
        "por_tipo": {
            coluna: round(periodo[coluna].sum(), 2) for coluna in colunas_desconto
        },
        "mensal": [
            {
                "mes_ano": f"{mes}/{ano}",
                "INSS (R$)": round(inss, 2),
                "IRRF (R$)": round(irrf, 2),
                "Plano de Saúde": round(saude, 2)
            }
            for mes, ano, inss, irrf, saude in zip(
                periodo["Mês"].astype(str),
                periodo["Ano"].astype(str),
                periodo["INSS (R$)"],
                periodo["IRRF (R$)"],
                periodo["Plano de Saúde"]
            )
        ]
    }

    return resumo

def get_Resumo_Vencimentos_Periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna um resumo detalhado dos vencimentos por tipo e por mês, dentro de um período especificado."""

    colunas_vencimentos = ["Salário Base", "Comissão", "Bonificações", "Horas Extras", "Valores Adicionais"]

    for coluna in colunas_vencimentos:
        if coluna not in df.columns:
            return {"erro": f"A coluna de vencimento '{coluna}' não foi encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_inicial_num = mes_map.get(mes_inicial.capitalize())
    mes_final_num = mes_map.get(mes_final.capitalize())

    if mes_inicial_num is None or mes_final_num is None:
        return {"erro": "Mês inicial ou final inválido."}

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

    resumo = {
        "total_vencimentos": round(periodo[colunas_vencimentos].sum().sum(), 2),
        "por_tipo": {
            coluna: round(periodo[coluna].sum(), 2) for coluna in colunas_vencimentos
        },
        "mensal": [
            {
                "mes_ano": f"{mes}/{ano}",
                "Salário Base": round(sb, 2),
                "Comissão": round(c, 2),
                "Bonificações": round(b, 2),
                "Horas Extras": round(he, 2),
                "Valores Adicionais": round(va, 2)
            }
            for mes, ano, sb, c, b, he, va in zip(
                periodo["Mês"].astype(str),
                periodo["Ano"].astype(str),
                periodo["Salário Base"],
                periodo["Comissão"],
                periodo["Bonificações"],
                periodo["Horas Extras"],
                periodo["Valores Adicionais"]
            )
        ]
    }

    return resumo

def get_Resumo_Folha_Periodo(mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    """Retorna um resumo completo da folha de pagamento (vencimentos, descontos e líquido) no período especificado."""

    col_venc = ["Salário Base", "Comissão", "Bonificações", "Horas Extras", "Valores Adicionais"]
    col_desc = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]

    for coluna in col_venc + col_desc:
        if coluna not in df.columns:
            return {"erro": f"A coluna '{coluna}' não foi encontrada na base de dados."}

    mes_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_ini_num = mes_map.get(mes_inicial.capitalize())
    mes_fim_num = mes_map.get(mes_final.capitalize())

    if mes_ini_num is None or mes_fim_num is None:
        return {"erro": "Mês inicial ou final inválido."}

    dados_ordenados = df.sort_values(by=["Ano", "Mês"])

    periodo = dados_ordenados[
        (dados_ordenados["Ano"] > ano_inicial) |
        ((dados_ordenados["Ano"] == ano_inicial) & (dados_ordenados["Mês"] >= mes_ini_num))
    ]
    periodo = periodo[
        (periodo["Ano"] < ano_final) |
        ((periodo["Ano"] == ano_final) & (periodo["Mês"] <= mes_fim_num))
    ]

    if periodo.empty:
        return {"erro": "Nenhum dado encontrado no período especificado."}

    resumo = {
        "total_vencimentos": round(periodo[col_venc].sum().sum(), 2),
        "total_descontos": round(periodo[col_desc].sum().sum(), 2),
        "liquido_a_receber": round(periodo["Líquido a Receber"].sum(), 2),
        "por_tipo_vencimento": {
            coluna: round(periodo[coluna].sum(), 2) for coluna in col_venc
        },
        "por_tipo_desconto": {
            coluna: round(periodo[coluna].sum(), 2) for coluna in col_desc
        },
        "mensal": [
            {
                "mes_ano": f"{mes}/{ano}",
                "vencimentos": round(sum([linha[c] for c in col_venc]), 2),
                "descontos": round(sum([linha[c] for c in col_desc]), 2),
                "liquido": round(linha["Líquido a Receber"], 2)
            }
            for _, linha in periodo.iterrows()
            for mes, ano in [(str(linha["Mês"]), str(linha["Ano"]))]
        ]
    }

    return resumo
