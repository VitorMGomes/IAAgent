from openai import OpenAI
from pydantic import BaseModel
from datetime import date
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Colaborador(BaseModel):
    nome: str
    email: str
    profissao: str
    mes: str
    ano: int
    salario_base: float
    comissao: float
    adicionais: float
    bonificacoes: float
    total_vencimentos: float
    desconto_inss: float
    desconto_irrf: float
    plano_saude: float
    total_descontos: float
    salario_liquido: float
    carga_horaria: int
    horas_extras: int
    fgts_base: float
    fgts_mes: float


completion = client.beta.chat.completions.parse(
    model="gpt-4.1-nano-2025-04-14",
    messages=[
        {"role": "system", "content": "Você é um assistente que ajuda sobre folhas de pagamento da empresa"},
        {
            "role": "user",
            "content": "A colaboradora Ana Silva (ana.silva@email.com) trabalhou como Analista de Sistemas no mês de Jan-2020. Seu salário base foi de R$2641.00, com R$332.00 de comissão, R$231.00 de valores adicionais e R$476.00 de bonificações. O total bruto (vencimentos) foi de R$3680.00. Foram aplicados descontos de INSS (9.15% → R$336.72) e IRRF (7.5% → R$276.00),  além do plano de saúde (R$273.00). O total de descontos foi R$885.72.  Ela recebeu R$2794.28 líquidos, com uma carga horária de 44 horas e 0 horas extras. A base do FGTS foi R$3680.00, com depósito do mês em R$294.40."
            
        },
    ],
    response_format=Colaborador,
)

event = completion.choices[0].message.parsed

print(f"Nome: {event.nome}")
print(f"E-mail: {event.email}")
print(f"Profissão: {event.profissao}")
print(f"Mês: {event.mes}")
print(f"Ano: {event.ano}")
print(f"Salário Base: R${event.salario_base:.2f}")
print(f"Comissão: R${event.comissao:.2f}")
print(f"Adicionais: R${event.adicionais:.2f}")
print(f"Bonificações: R${event.bonificacoes:.2f}")
print(f"Total Vencimentos: R${event.total_vencimentos:.2f}")
print(f"Desconto INSS: R${event.desconto_inss:.2f}")
print(f"Desconto IRRF: R${event.desconto_irrf:.2f}")
print(f"Plano de Saúde: R${event.plano_saude:.2f}")
print(f"Total Descontos: R${event.total_descontos:.2f}")
print(f"Salário Líquido: R${event.salario_liquido:.2f}")
print(f"Carga Horária: {event.carga_horaria} horas")
print(f"Horas Extras: {event.horas_extras} horas")
print(f"Base FGTS: R${event.fgts_base:.2f}")
print(f"Depósito FGTS do mês: R${event.fgts_mes:.2f}")
