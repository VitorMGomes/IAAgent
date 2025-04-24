
import re
from staticFuncs import *

# Mapeamento direto (para funções sem parâmetros dinâmicos)
dispatcher = {
    "salario_bruto_total": salario_bruto_total,
    "crescimento_salario_liquido": crescimento_salario_liquido,
    "horas_extras_total": horas_extras_total,
    "media_total_descontos": media_total_descontos,
    "total_descontos": total_descontos,
    "salario_bruto_em_mes": salario_bruto_em_mes,
    "horas_extras_periodo": horas_extras_periodo,
    "variacao_salario_base": variacao_salario_base,
    "media_salario_bruto": media_salario_bruto,
    "media_salario_liquido": media_salario_liquido,
    "total_irrf_pago": total_irrf_pago,
    "total_inss_pago": total_inss_pago,
    "percentual_liquido_sobre_bruto": percentual_liquido_sobre_bruto,
    "media_horas_extras": media_horas_extras,
    "total_horas_extras_por_ano": total_horas_extras_por_ano,
    "comparar_liquido_entre_meses": comparar_liquido_entre_meses,
    "maior_salario_bruto": maior_salario_bruto,
    "mes_maior_liquido": mes_maior_liquido,
    "maior_desconto_percentual": maior_desconto_percentual,
    "meses_liquido_acima_percentual": meses_liquido_acima_percentual,
    "meses_com_bonificacao_acima": meses_com_bonificacao_acima,
    "inss_em_mes_ano": inss_em_mes_ano,
    "irrf_em_mes_ano": irrf_em_mes_ano,
    "total_fgts_ano": total_fgts_ano,
    "meses_com_liquido_maior_que": meses_com_liquido_maior_que
}

def extrair_mes_ano(mensagem: str):
    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
    }
    match = re.search(r"(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+(\d{4})", mensagem.lower())
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def extrair_valor(mensagem: str):
    match = re.search(r"\d+(?:[.,]\d+)?", mensagem)
    if match:
        return float(match.group(0).replace(",", "."))
    return None

def identificar_intencao(mensagem: str):
    mensagem = mensagem.lower()

    if "salário bruto" in mensagem and "últimos" in mensagem:
        return "salario_bruto_total", {"n_meses": 3}

    if "crescimento" in mensagem and "líquido" in mensagem:
        return "crescimento_salario_liquido", {"n_meses": 3}

    if "horas extras" in mensagem and "total" in mensagem:
        return "horas_extras_total", {}

    if "média de descontos" in mensagem:
        return "media_total_descontos", {"n_meses": 3}

    if "total de descontos" in mensagem:
        return "total_descontos", {"n_meses": 3}

    if "média do salário líquido" in mensagem:
        return "media_salario_liquido", {"n_meses": 3}

    if "média do salário bruto" in mensagem:
        return "media_salario_bruto", {"n_meses": 3}

    if "irrf" in mensagem:
        mes, ano = extrair_mes_ano(mensagem)
        if mes and ano:
            return "irrf_em_mes_ano", {"mes": mes, "ano": ano}

    if "inss" in mensagem:
        mes, ano = extrair_mes_ano(mensagem)
        if mes and ano:
            return "inss_em_mes_ano", {"mes": mes, "ano": ano}

    if "fgts" in mensagem and "total" in mensagem:
        match = re.search(r"\d{4}", mensagem)
        if match:
            return "total_fgts_ano", {"ano": int(match.group(0))}

    if "bonificações" in mensagem and "acima" in mensagem:
        valor = extrair_valor(mensagem)
        if valor:
            return "meses_com_bonificacao_acima", {"valor": valor}

    if "líquido" in mensagem and "acima de" in mensagem:
        valor = extrair_valor(mensagem)
        if valor:
            return "meses_com_liquido_maior_que", {"valor": valor}

    if "líquido" in mensagem and "%" in mensagem:
        percentual = extrair_valor(mensagem)
        if percentual:
            return "meses_liquido_acima_percentual", {"percentual": percentual}

    if "maior salário" in mensagem:
        return "maior_salario_bruto", {}

    if "maior líquido" in mensagem:
        return "mes_maior_liquido", {}

    if "maior desconto proporcional" in mensagem:
        return "maior_desconto_percentual", {}

    return None, {}
