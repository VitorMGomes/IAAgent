import os
import pandas as pd
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Carrega variáveis de ambiente e dados
load_dotenv()

# Caminho absoluto até o CSV
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "data", "Dados.csv")

# Carrega o CSV
df = pd.read_csv(csv_path)

# Normaliza meses para números
mes_map = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}
df["Mês"] = df["Mês"].map(mes_map)

# Configuração do RAG
chroma_dir = os.path.join(base_dir, "chrome_langchain_db")
retriever = Chroma(
    persist_directory=chroma_dir,
    embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
).as_retriever()
rag_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    retriever=retriever,
    return_source_documents=False
)

# ---------- SCHEMAS e DECORATOR PARA INSIGHTS ----------
from pydantic import BaseModel
from typing import List, Literal, Any, Dict

class InsightSchema(BaseModel):
    tipo: Literal["linha", "barra", "pizza"]
    titulo: str
    eixo_x: List[str]
    eixo_y: str
    dados: List[Any]

class BatchInsights(BaseModel):
    insights: List[InsightSchema]


def normalize_insights(func):
    def wrapper(*args, **kwargs):
        raw = func(*args, **kwargs)
        if isinstance(raw, dict) and raw.get("erro"):
            return raw
        if isinstance(raw, dict) and "insights" not in raw:
            raw = {"insights": [raw]}
        batch = BatchInsights(**raw)
        return batch.dict()
    return wrapper

# ---------- FUNÇÕES DE CONSULTA E INSIGHTS ----------

def consultar_documento_txt_ou_pdf(pergunta: str) -> dict:
    resposta = rag_chain.run(pergunta)
    return {"resposta": resposta}

@normalize_insights
def get_informacoesCabecalho() -> dict:
    cols = df.columns.tolist()
    return {
        "tipo": "pizza",
        "titulo": "Colunas Disponíveis",
        "eixo_x": [],
        "eixo_y": "",
        "dados": [{"label": c, "value": 0} for c in cols]
    }

@normalize_insights
def get_Media(coluna: str) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    valores = df[coluna].dropna().round(2)
    meses = [str(i+1) for i in range(len(valores))]
    return {
        "tipo": "linha",
        "titulo": f"Média de {coluna}",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": [float(v) for v in valores]
    }

@normalize_insights
def get_Media_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    mi, mf = mes_map.get(mes_inicial.capitalize()), mes_map.get(mes_final.capitalize())
    if not mi or not mf:
        return {"erro": "Mês inválido."}
    dfp = df.sort_values(["Ano","Mês"])
    mask = ((dfp["Ano"]>ano_inicial) | ((dfp["Ano"]==ano_inicial)&(dfp["Mês"]>=mi))) & \
           ((dfp["Ano"]<ano_final)  | ((dfp["Ano"]==ano_final)  &(dfp["Mês"]<=mf)))
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Sem dados no período."}
    meses = [f"{m}/{a}" for m,a in zip(sel["Mês"], sel["Ano"])]
    vals = [round(v,2) for v in sel[coluna]]
    media = round(sum(vals)/len(vals),2)
    return {
        "tipo": "linha",
        "titulo": f"Média de {coluna} ({mes_inicial}/{ano_inicial}-{mes_final}/{ano_final})",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Media_Ultimo(coluna: str, meses: int) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    sel = df.sort_values(["Ano","Mês"]).tail(meses)
    if sel.empty:
        return {"erro": "Sem dados suficientes."}
    meses_l = [f"{m}/{a}" for m,a in zip(sel["Mês"], sel["Ano"])]
    vals = [round(v,2) for v in sel[coluna]]
    return {
        "tipo": "linha",
        "titulo": f"Média últimos {meses} meses de {coluna}",
        "eixo_x": meses_l,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Maior(coluna: str) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    sel = df.sort_values(["Ano","Mês"])
    idx = sel[coluna].idxmax(); lin = sel.loc[idx]
    meses_l = [f"{m}/{a}" for m,a in zip(sel["Mês"], sel["Ano"])]
    vals = [round(v,2) for v in sel[coluna]]
    titulo = f"Maior {coluna}: {round(lin[coluna],2)} em {int(lin['Mês'])}/{int(lin['Ano'])}"
    return {
        "tipo": "linha",
        "titulo": titulo,
        "eixo_x": meses_l,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Maior_Periodo(coluna: str, mes_inicial: str, ano_inicial: int, mes_final: str, ano_final: int) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    mi, mf = mes_map.get(mes_inicial.capitalize()), mes_map.get(mes_final.capitalize())
    if not mi or not mf:
        return {"erro": "Mês inválido."}
    dfp = df.sort_values(["Ano","Mês"])
    mask = ((dfp["Ano"]>ano_inicial) | ((dfp["Ano"]==ano_inicial)&(dfp["Mês"]>=mi))) & \
           ((dfp["Ano"]<ano_final)  | ((dfp["Ano"]==ano_final)  &(dfp["Mês"]<=mf)))
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Sem dados no período."}
    idx = sel[coluna].idxmax(); lin = sel.loc[idx]
    meses_l = [f"{m}/{a}" for m,a in zip(sel["Mês"], sel["Ano"])]
    vals = [round(v,2) for v in sel[coluna]]
    titulo = f"Maior {coluna} no período: {round(lin[coluna],2)} em {int(lin['Mês'])}/{int(lin['Ano'])}"
    return {
        "tipo": "linha",
        "titulo": titulo,
        "eixo_x": meses_l,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Maior_Ultimo(coluna: str, meses: int) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    sel = df.sort_values(["Ano","Mês"]).tail(meses)
    if sel.empty:
        return {"erro": "Sem dados suficientes."}
    idx = sel[coluna].idxmax(); lin = sel.loc[idx]
    meses_l = [f"{m}/{a}" for m,a in zip(sel["Mês"], sel["Ano"])]
    vals = [round(v,2) for v in sel[coluna]]
    titulo = f"Maior {coluna} últimos {meses} meses: {round(lin[coluna],2)} em {int(lin['Mês'])}/{int(lin['Ano'])}"
    return {
        "tipo": "linha",
        "titulo": titulo,
        "eixo_x": meses_l,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Total(coluna: str) -> dict:
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada."}
    meses_l = [f"{m}/{a}" for m,a in zip(df["Mês"], df["Ano"])]
    vals = [round(v,2) for v in df[coluna]]
    total = round(sum(vals),2)
    return {
        "tipo": "barra",
        "titulo": f"Total {coluna}: {total}",
        "eixo_x": meses_l,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Total_Periodo(
    coluna: str,
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna os valores mensais e o total acumulado da coluna especificada
    entre mes_inicial/ano_inicial e mes_final/ano_final, formatados como um insight.
    """
    # valida coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # converte meses
    mi = mes_map.get(mes_inicial.capitalize())
    mf = mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) |
         ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) |
         ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # monta listas para o gráfico
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]
    total_acumulado = round(sum(valores), 2)

    return {
        "tipo": "barra",
        "titulo": f"Total de {coluna} de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}: {total_acumulado}",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": valores
    }

@normalize_insights
def get_Total_Ultimo(coluna: str, meses: int) -> dict:
    """
    Retorna a soma dos valores da coluna especificada nos últimos N meses,
    formatado como um insight de barra com dados mensais e total acumulado.
    """
    # Validação da coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Seleciona os últimos N meses
    sel = df.sort_values(["Ano", "Mês"]).tail(meses)
    if sel.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    # Prepara eixos e valores
    meses_x = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]
    total = round(sum(valores), 2)

    # Retorna o insight padronizado
    return {
        "tipo": "barra",
        "titulo": f"Total de {coluna} – últimos {meses} meses: {total}",
        "eixo_x": meses_x,
        "eixo_y": coluna,
        "dados": valores
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

@normalize_insights
def get_Evolucao_Periodo(
    coluna: str,
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna a evolução mês a mês da coluna especificada dentro de um período,
    formatada como um insight de linha.
    """
    # valida coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # converte meses
    mi = mes_map.get(mes_inicial.capitalize())
    mf = mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) |
         ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) |
         ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # prepara eixos e valores
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]

    # retorna insight padronizado
    return {
        "tipo": "linha",
        "titulo": f"Evolução de {coluna} de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": valores
    }

@normalize_insights
def get_Mes_Ano(coluna: str, mes: str, ano: int) -> dict:
    """
    Retorna o valor da coluna em um mês e ano específicos,
    formatado como um insight de pizza (único valor destacado).
    """
    # Validação da coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # Converte o nome do mês
    mi = mes_map.get(mes.capitalize())
    if mi is None:
        return {"erro": f"Mês '{mes}' inválido."}

    # Filtra o mês/ano desejado
    sel = df[(df["Mês"] == mi) & (df["Ano"] == ano)]
    if sel.empty:
        return {"erro": f"Nenhum dado encontrado para {mes}/{ano}."}

    # Extrai o valor
    valor = round(sel[coluna].iloc[0], 2)

    # Retorna insight padronizado
    return {
        "tipo": "pizza",
        "titulo": f"{coluna} em {mes}/{ano}: {valor}",
        "eixo_x": [],
        "eixo_y": "",
        "dados": [{"label": coluna, "value": valor}]
    }

@normalize_insights
def get_Crescimento_Percentual(coluna: str) -> dict:
    """
    Retorna o crescimento percentual da coluna do primeiro até o último mês,
    formatado como um insight de barra com o valor inicial e final.
    """
    # valida coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # ordena cronologicamente
    sel = df.sort_values(["Ano", "Mês"])
    if len(sel) < 2:
        return {"erro": "Não há dados suficientes para calcular crescimento percentual."}

    # extrai valores
    valor_inicial = sel[coluna].iloc[0]
    valor_final   = sel[coluna].iloc[-1]
    if valor_inicial == 0:
        return {"erro": "Valor inicial é zero, não é possível calcular variação percentual."}

    # calcula crescimento
    crescimento = round(((valor_final - valor_inicial) / valor_inicial) * 100, 2)

    # monta insight
    mes_ini = f"{int(sel['Mês'].iloc[0])}/{int(sel['Ano'].iloc[0])}"
    mes_fin = f"{int(sel['Mês'].iloc[-1])}/{int(sel['Ano'].iloc[-1])}"
    return {
        "tipo": "barra",
        "titulo": f"Crescimento de {coluna}: {crescimento}%",
        "eixo_x": [mes_ini, mes_fin],
        "eixo_y": coluna,
        "dados": [round(valor_inicial, 2), round(valor_final, 2)]
    }

@normalize_insights
def get_Crescimento_Percentual_Periodo(
    coluna: str,
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna o crescimento percentual da coluna dentro de um período,
    formatado como um insight de barra com todos os valores mensais e o percentual.
    """
    # validação da coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # converte meses
    mi = mes_map.get(mes_inicial.capitalize())
    mf = mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) |
         ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) |
         ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty or len(sel) < 2:
        return {"erro": "Período inválido ou com dados insuficientes para calcular o crescimento."}

    # calcula crescimento
    inicial = sel[coluna].iloc[0]
    final   = sel[coluna].iloc[-1]
    if inicial == 0:
        return {"erro": "Valor inicial é zero; não é possível calcular variação percentual."}
    pct     = round(((final - inicial) / inicial) * 100, 2)

    # prepara eixos e valores
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    vals  = [round(v, 2) for v in sel[coluna]]

    # monta insight
    return {
        "tipo": "barra",
        "titulo": f"Crescimento de {coluna} de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}: {pct}%",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": vals
    }

@normalize_insights
def get_Menor(coluna: str) -> dict:
    """
    Retorna o menor valor da coluna especificada, juntamente com todos os dados individuais,
    formatado como um insight de linha destacando o valor mínimo.
    """
    # valida coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # encontra o índice do menor valor
    sel = df.sort_values(["Ano", "Mês"])
    idx = sel[coluna].idxmin()
    linha = sel.loc[idx]

    # lista de meses e valores
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]

    # título com o menor valor e sua data
    valor_min = round(linha[coluna], 2)
    mes_min   = int(linha["Mês"])
    ano_min   = int(linha["Ano"])
    titulo = f"Menor {coluna}: {valor_min} em {mes_min}/{ano_min}"

    return {
        "tipo": "linha",
        "titulo": titulo,
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": valores
    }

@normalize_insights
def get_Menor_Periodo(
    coluna: str,
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna o menor valor da coluna especificada dentro de um período,
    com dados mensais, formatado como um insight de linha.
    """
    # validação da coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # converte meses
    mi = mes_map.get(mes_inicial.capitalize())
    mf = mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra e ordena período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) |
         ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) |
         ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # lista de meses e valores
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]

    # encontra o menor valor e sua posição
    idx = sel[coluna].idxmin()
    linha = sel.loc[idx]
    valor_min = round(linha[coluna], 2)
    mes_min   = int(linha["Mês"])
    ano_min   = int(linha["Ano"])

    # monta insight
    return {
        "tipo": "linha",
        "titulo": f"Menor {coluna} de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}: {valor_min} em {mes_min}/{ano_min}",
        "eixo_x": meses,
        "eixo_y": coluna,
        "dados": valores
    }

@normalize_insights
def get_Menor_Ultimo(coluna: str, meses: int) -> dict:
    """
    Retorna o menor valor da coluna especificada nos últimos N meses,
    formatado como um insight de linha com os dados mensais e destaque do mínimo.
    """
    # validação da coluna
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não encontrada na base de dados."}

    # seleciona e ordena os últimos N meses
    sel = df.sort_values(["Ano", "Mês"]).tail(meses)
    if sel.empty:
        return {"erro": "Não há dados suficientes para os últimos meses especificados."}

    # prepara eixos e valores
    meses_x = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    valores = [round(v, 2) for v in sel[coluna]]

    # encontra o menor valor e sua data
    idx_min = sel[coluna].idxmin()
    linha_min = sel.loc[idx_min]
    valor_min = round(linha_min[coluna], 2)
    mes_min   = int(linha_min["Mês"])
    ano_min   = int(linha_min["Ano"])

    # título destacando o mínimo
    titulo = f"Menor {coluna} — últimos {meses} meses: {valor_min} em {mes_min}/{ano_min}"

    return {
        "tipo": "linha",
        "titulo": titulo,
        "eixo_x": meses_x,
        "eixo_y": coluna,
        "dados": valores
    }

@normalize_insights
def get_Resumo_Descontos_Periodo(
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna um batch de insights com:
    1) pizza de Descontos por Tipo no período
    2) linha da evolução mensal do total de descontos
    """
    # valida colunas
    colunas = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]
    for c in colunas:
        if c not in df.columns:
            return {"erro": f"A coluna de desconto '{c}' não foi encontrada na base de dados."}
    # converte meses
    mi, mf = mes_map.get(mes_inicial.capitalize()), mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}
    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) | ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) | ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}
    # cálculo por tipo
    soma_por_tipo = {c: round(sel[c].sum(), 2) for c in colunas}
    # cálculo mensal total
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    totais = [round(sel.loc[i, colunas].sum(), 2) for i in sel.index]
    # monta insights
    insight_tipo = {
        "tipo": "pizza",
        "titulo": f"Descontos por Tipo de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}",
        "eixo_x": [],
        "eixo_y": "",
        "dados": [{"label": k, "value": v} for k, v in soma_por_tipo.items()]
    }
    insight_mensal = {
        "tipo": "linha",
        "titulo": f"Evolução Mensal dos Descontos ({mes_inicial}/{ano_inicial}–{mes_final}/{ano_final})",
        "eixo_x": meses,
        "eixo_y": "Total Descontos (R$)",
        "dados": totais
    }
    return {"insights": [insight_tipo, insight_mensal]}

@normalize_insights
def get_Resumo_Vencimentos_Periodo(
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna um batch de insights com:
    1) pizza de Vencimentos por Tipo no período
    2) linha da evolução mensal do total de vencimentos
    """
    # valida colunas de vencimento
    cols = ["Salário Base", "Comissão", "Bonificações", "Horas Extras", "Valores Adicionais"]
    for c in cols:
        if c not in df.columns:
            return {"erro": f"A coluna de vencimento '{c}' não foi encontrada na base de dados."}

    # converte meses
    mi, mf = mes_map.get(mes_inicial.capitalize()), mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) | ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) | ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado dentro do período especificado."}

    # soma por tipo de vencimento
    soma_tipo = {c: round(sel[c].sum(), 2) for c in cols}
    # evolução mensal total
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    totais = [round(sel.loc[i, cols].sum(), 2) for i in sel.index]

    insight_tipo = {
        "tipo": "pizza",
        "titulo": f"Vencimentos por Tipo de {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}",
        "eixo_x": [],
        "eixo_y": "",
        "dados": [{"label": k, "value": v} for k, v in soma_tipo.items()]
    }
    insight_mensal = {
        "tipo": "linha",
        "titulo": f"Evolução Mensal dos Vencimentos ({mes_inicial}/{ano_inicial}–{mes_final}/{ano_final})",
        "eixo_x": meses,
        "eixo_y": "Total Vencimentos (R$)",
        "dados": totais
    }

    return {"insights": [insight_tipo, insight_mensal]}

@normalize_insights
def get_Resumo_Folha_Periodo(
    mes_inicial: str,
    ano_inicial: int,
    mes_final: str,
    ano_final: int
) -> dict:
    """
    Retorna um batch de insights com:
    1) pizza de Resumo Geral (vencimentos × descontos × líquido)
    2) pizza de Vencimentos por Tipo
    3) pizza de Descontos por Tipo
    4) linha de Líquido Mês a Mês
    """
    # valida colunas
    col_venc = ["Salário Base", "Comissão", "Bonificações", "Horas Extras", "Valores Adicionais"]
    col_desc = ["INSS (R$)", "IRRF (R$)", "Plano de Saúde"]
    for c in col_venc + col_desc:
        if c not in df.columns:
            return {"erro": f"A coluna '{c}' não foi encontrada na base de dados."}

    # converte meses
    mi = mes_map.get(mes_inicial.capitalize())
    mf = mes_map.get(mes_final.capitalize())
    if mi is None or mf is None:
        return {"erro": "Mês inicial ou final inválido."}

    # filtra período
    dfp = df.sort_values(["Ano", "Mês"])
    mask = (
        ((dfp["Ano"] > ano_inicial) |
         ((dfp["Ano"] == ano_inicial) & (dfp["Mês"] >= mi)))
        &
        ((dfp["Ano"] < ano_final) |
         ((dfp["Ano"] == ano_final) & (dfp["Mês"] <= mf)))
    )
    sel = dfp[mask]
    if sel.empty:
        return {"erro": "Nenhum dado encontrado no período especificado."}

    # cálculos gerais
    total_v = round(sel[col_venc].sum().sum(), 2)
    total_d = round(sel[col_desc].sum().sum(), 2)
    total_l = round(sel["Líquido a Receber"].sum(), 2)

    # 1) pizza resumo geral
    insight1 = {
        "tipo": "pizza",
        "titulo": f"Resumo Geral {mes_inicial}/{ano_inicial}–{mes_final}/{ano_final}",
        "eixo_x": [],
        "eixo_y": "",
        "dados": [
            {"label": "Vencimentos", "value": total_v},
            {"label": "Descontos",   "value": total_d},
            {"label": "Líquido",      "value": total_l},
        ]
    }

    # 2) pizza vencimentos por tipo
    insight2 = {
        "tipo": "pizza",
        "titulo": f"Vencimentos por Tipo ({mes_inicial}/{ano_inicial}–{mes_final}/{ano_final})",
        "eixo_x": [], "eixo_y": "",
        "dados": [
            {"label": c, "value": round(sel[c].sum(), 2)}
            for c in col_venc
        ]
    }

    # 3) pizza descontos por tipo
    insight3 = {
        "tipo": "pizza",
        "titulo": f"Descontos por Tipo ({mes_inicial}/{ano_inicial}–{mes_final}/{ano_final})",
        "eixo_x": [], "eixo_y": "",
        "dados": [
            {"label": c, "value": round(sel[c].sum(), 2)}
            for c in col_desc
        ]
    }

    # 4) linha líquido mês a mês
    meses = [f"{m}/{a}" for m, a in zip(sel["Mês"], sel["Ano"])]
    liquidos = [round(v, 2) for v in sel["Líquido a Receber"]]
    insight4 = {
        "tipo": "linha",
        "titulo": f"Líquido Mês a Mês ({mes_inicial}/{ano_inicial}–{mes_final}/{ano_final})",
        "eixo_x": meses,
        "eixo_y": "Líquido (R$)",
        "dados": liquidos
    }

    return {"insights": [insight1, insight2, insight3, insight4]}


@normalize_insights
def get_Participacao_Vencimentos(
    colunas: List[str],
    mes: str,
    ano: int
) -> dict:
    """
    Gera um insight de pizza com a participação percentual
    de cada coluna de vencimento em um mês/ano específico.
    """
    # converte mês
    mes_num = mes_map.get(mes.capitalize())
    if mes_num is None:
        return {"erro": f"Mês '{mes}' inválido."}

    linha = df[(df["Mês"] == mes_num) & (df["Ano"] == ano)]
    if linha.empty:
        return {"erro": f"Sem dados para {mes}/{ano}."}

    linha = linha.iloc[0]
    dados = []
    for col in colunas:
        if col in df.columns:
            dados.append({"label": col, "value": round(linha[col], 2)})
        else:
            return {"erro": f"Coluna '{col}' não existe."}

    titulo = f"Participação dos vencimentos em {mes}/{ano}"
    return {
        "tipo": "pizza",
        "titulo": titulo,
        "eixo_x": [],
        "eixo_y": "",
        "dados": dados
    }
