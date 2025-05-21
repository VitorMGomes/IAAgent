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
            "description": "Nome da coluna a ser analisada (ex: 'Comissão', 'Plano de Saúde')."
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
            "description": "Quantidade de meses a considerar a partir do fim."
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
        "additionalProperties": False
      },
      "strict": True
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
            "description": "Nome da coluna a ser avaliada (ex: 'Comissão', 'Total Vencimentos')"
          }
        },
        "required": ["coluna"],
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
        "required": ["coluna", "mes_inicial", "ano_inicial", "mes_final", "ano_final"],
        "additionalProperties": False
      },
      "strict": True
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_menor_ultimo",
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
        "required": ["coluna", "meses"],
        "additionalProperties": False
      },
      "strict": True
    }
  }
]
