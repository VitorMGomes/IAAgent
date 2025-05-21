from functions.folha_tools import *


def call_function(name: str, args: dict):
    if name == "consultar_documento_txt_ou_pdf":
        return consultar_documento_txt_ou_pdf(**args)
    elif name == "get_informacoesCabecalho":
        return get_informacoesCabecalho()
    elif name == "get_Media":
        return get_Media(**args)
    elif name == "get_Media_Periodo":
        return get_Media_Periodo(**args)
    elif name == "get_Media_Ultimo":
        return get_Media_Ultimo(**args)
    elif name == "get_Maior":
        return get_Maior(**args)
    elif name == "get_Maior_Periodo":
        return get_Maior_Periodo(**args)
    elif name == "get_maior_ultimo":
        return get_maior_ultimo(**args)
    elif name == "get_total":
        return get_total(**args)
    elif name == "get_total_Periodo":
        return get_total_Periodo(**args)
    elif name == "get_total_ultimo":
        return get_total_ultimo(**args)
    elif name == "get_evolucao":
        return get_evolucao(**args)
    elif name == "get_evolucao_Periodo":
        return get_evolucao_Periodo(**args)
    elif name == "get_mes_ano":
        return get_mes_ano(**args)
    elif name == "get_crescimento_percentual":
        return get_crescimento_percentual(**args)
    elif name == "get_crescimento_percentual_periodo":
        return get_crescimento_percentual_periodo(**args)
    elif name == "get_total_descontos":
        return get_total_descontos()
    elif name == "get_total_descontos_Periodo":
        return get_total_descontos_Periodo(**args)
    elif name == "get_Menor":
        return get_Menor(**args)
    elif name == "get_menor_ultimo":
        return get_menor_ultimo(**args)
    elif name == "get_Menor_Periodo":
        return get_Menor_Periodo(**args)
    else:
        return {"erro": f"Função '{name}' não reconhecida no dispatcher."}
