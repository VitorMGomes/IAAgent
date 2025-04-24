import pandas as pd


def processar_dados(df: pd.DataFrame) -> pd.DataFrame:

    # //===================================================================//
    # Transformando as colunas de texto para FLOAT                        //
    # //===================================================================//
    colunas_float = [
        "Salário Base",
        "Comissão",
        "Valores Adicionais",
        "Bonificações",
        "Total Vencimentos",
        "INSS (R$)",
        "IRRF (R$)",
        "Plano de Saúde",
        "Total Descontos",
        "Líquido a Receber",
        "FGTS do Mês",
        "Base FGTS",
        "Base INSS",
        "Base IRRF",
    ]

    for col in colunas_float:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # //===================================================================//
    # Transformando as colunas de texto para %                            //
    # //===================================================================//
    colunas_porcentagem = ["INSS (%)", "IRRF (%)"]
    for col in colunas_porcentagem:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # //===================================================================//
    # Transformando as colunas de texto para INT                          //
    # //===================================================================//
    for col in ["Carga Horária", "Horas Extras"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # //===================================================================//
    # Ordenando o DataFrame por data                                      //
    # //===================================================================//
    if "Mês/Ano" in df.columns:
        df["Data"] = pd.to_datetime(df["Mês/Ano"], format="%b-%Y")

    if "Data" in df.columns:
        df = df.sort_values("Data").reset_index(drop=True)

    return df
