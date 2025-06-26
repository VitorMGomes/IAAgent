from .folha_tools import *


def call_function(name: str, arguments: dict) -> dict:
    try:
        match name:
            case "consultar_documento_txt_ou_pdf":
                return consultar_documento_txt_ou_pdf(**arguments)
            case "get_informacoesCabecalho":
                return get_informacoesCabecalho()
            case "get_Media":
                return get_Media(**arguments)
            case "get_Media_Periodo":
                return get_Media_Periodo(**arguments)
            case "get_Media_Ultimo":
                return get_Media_Ultimo(**arguments)
            case "get_Maior":
                return get_Maior(**arguments)
            case "get_Maior_Periodo":
                return get_Maior_Periodo(**arguments)
            case "get_Maior_Ultimo":
                return get_Maior_Ultimo(**arguments)
            case "get_Menor":
                return get_Menor(**arguments)
            case "get_Menor_Periodo":
                return get_Menor_Periodo(**arguments)
            case "get_Menor_Ultimo":
                return get_Menor_Ultimo(**arguments)
            case "get_Total":
                return get_Total(**arguments)
            case "get_Total_Periodo":
                return get_Total_Periodo(**arguments)
            case "get_Total_Ultimo":
                return get_Total_Ultimo(**arguments)
            case "get_Evolucao":
                return get_Evolucao(**arguments)
            case "get_Evolucao_Periodo":
                return get_Evolucao_Periodo(**arguments)
            case "get_Mes_Ano":
                return get_Mes_Ano(**arguments)
            case "get_Crescimento_Percentual":
                return get_Crescimento_Percentual(**arguments)
            case "get_Crescimento_Percentual_Periodo":
                return get_Crescimento_Percentual_Periodo(**arguments)
            case "get_Resumo_Descontos_Periodo":
                return get_Resumo_Descontos_Periodo(**arguments)
            case "get_Resumo_Vencimentos_Periodo":
                return get_Resumo_Vencimentos_Periodo(**arguments)
            case "get_Resumo_Folha_Periodo":
                return get_Resumo_Folha_Periodo(**arguments)
            case "get_Participacao_Vencimentos":
                return  get_Participacao_Vencimentos(**arguments)
            case _:
                return {"erro": f"Função '{name}' não implementada."}
    except Exception as e:
        return {"erro": str(e)}
