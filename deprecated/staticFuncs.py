
import pandas as pd

def salario_bruto_total(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Total Vencimentos"].tail(n_meses).sum()

def crescimento_salario_liquido(df: pd.DataFrame, n_meses: int = 3) -> float:
    ultimos = df["Líquido a Receber"].tail(n_meses)
    if len(ultimos) < 2:
        return 0.0
    return round((ultimos.iloc[-1] - ultimos.iloc[0]) / ultimos.iloc[0] * 100, 2)

def horas_extras_total(df: pd.DataFrame) -> float:
    return df["Horas Extras"].sum()

def media_total_descontos(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Total Descontos"].tail(n_meses).mean()

def total_descontos(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Total Descontos"].tail(n_meses).sum()

def salario_bruto_em_mes(df: pd.DataFrame, mes_ano: str) -> float:
    dados_mes = df[df["Mês/Ano"] == mes_ano]
    return dados_mes["Total Vencimentos"].sum() if not dados_mes.empty else 0.0

def horas_extras_periodo(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Horas Extras"].tail(n_meses).sum()

def variacao_salario_base(df: pd.DataFrame) -> float:
    if len(df) < 2:
        return 0.0
    return round((df["Salário Base"].iloc[-1] - df["Salário Base"].iloc[0]) / df["Salário Base"].iloc[0] * 100, 2)

def media_salario_bruto(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Total Vencimentos"].tail(n_meses).mean()

def media_salario_liquido(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Líquido a Receber"].tail(n_meses).mean()

def total_irrf_pago(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["IRRF (R$)"].tail(n_meses).sum()

def total_inss_pago(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["INSS (R$)"].tail(n_meses).sum()

def percentual_liquido_sobre_bruto(df: pd.DataFrame, n_meses: int = 3) -> float:
    bruto = df["Total Vencimentos"].tail(n_meses)
    liquido = df["Líquido a Receber"].tail(n_meses)
    if len(bruto) == 0 or bruto.sum() == 0:
        return 0.0
    return round((liquido.sum() / bruto.sum()) * 100, 2)

def media_horas_extras(df: pd.DataFrame, n_meses: int = 3) -> float:
    return df["Horas Extras"].tail(n_meses).mean()

def total_horas_extras_por_ano(df: pd.DataFrame) -> dict:
    if "Data" not in df.columns:
        return {}
    return df.groupby(df["Data"].dt.year)["Horas Extras"].sum().to_dict()

def comparar_liquido_entre_meses(df: pd.DataFrame, mes_ano1: str, mes_ano2: str) -> float:
    valor1 = df[df["Mês/Ano"] == mes_ano1]["Líquido a Receber"].sum()
    valor2 = df[df["Mês/Ano"] == mes_ano2]["Líquido a Receber"].sum()
    return round(valor2 - valor1, 2)

def maior_salario_bruto(df: pd.DataFrame) -> float:
    """Retorna o maior valor de salário bruto (Total Vencimentos) recebido."""
    return df["Total Vencimentos"].max()
