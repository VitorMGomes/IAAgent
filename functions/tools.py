tools = [
    {
        "type": "function",
        "function": {
            "name": "consultar_documento_txt_ou_pdf",
            "description": "Consulta documentos TXT ou PDF indexados para responder perguntas não-numéricas sobre a folha.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {
                        "type": "string",
                        "description": "Pergunta sobre os documentos, como 'O que é FGTS?' ou 'Como funciona o IRRF?'"
                    }
                },
                "required": [
                    "pergunta"
                ],
                "additionalProperties": False
            },
            "strict": True
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
                "additionalProperties": False
            },
            "strict": True
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
                        "description": "Nome da coluna."
                    }
                },
                "required": [
                    "coluna"
                ],
                "additionalProperties": False
            },
            "strict": True
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
                "additionalProperties": False
            },
            "strict": True
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
                        "description": "Quantidade de meses a considerar."
                    }
                },
                "required": [
                    "coluna",
                    "meses"
                ],
                "additionalProperties": False
            },
            "strict": True
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
                "additionalProperties": False
            },
            "strict": True
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Maior_Ultimo",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Menor",
            "description": "Retorna o menor valor da coluna especificada junto com mês e ano.",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Menor_Periodo",
            "description": "Retorna o menor valor da coluna especificada dentro de um período, com mês e ano.",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Menor_Ultimo",
            "description": "Retorna o menor valor da coluna nos últimos N meses, com mês e ano.",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Total",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Total_Periodo",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Total_Ultimo",
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
                        "description": "Quantidade de meses a considerar."
                    }
                },
                "required": [
                    "coluna",
                    "meses"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Evolucao",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Evolucao_Periodo",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Mes_Ano",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Crescimento_Percentual",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Crescimento_Percentual_Periodo",
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
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Resumo_Descontos_Periodo",
            "description": "Retorna um resumo detalhado dos descontos por tipo e por mês, dentro de um período especificado.",
            "parameters": {
                "type": "object",
                "properties": {
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
                    "mes_inicial",
                    "ano_inicial",
                    "mes_final",
                    "ano_final"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Resumo_Vencimentos_Periodo",
            "description": "Retorna um resumo detalhado dos vencimentos por tipo e por mês, dentro de um período especificado.",
            "parameters": {
                "type": "object",
                "properties": {
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
                    "mes_inicial",
                    "ano_inicial",
                    "mes_final",
                    "ano_final"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_Resumo_Folha_Periodo",
            "description": "Retorna um resumo completo da folha de pagamento (vencimentos, descontos e líquido) no período especificado.",
            "parameters": {
                "type": "object",
                "properties": {
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
                    "mes_inicial",
                    "ano_inicial",
                    "mes_final",
                    "ano_final"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]