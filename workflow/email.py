import pandas as pd


data = pd.read_csv("../data/holerite.csv", sep=';')
#print(data)


email = "carlos.mendes@email.com"

colaborador = data[data["Email"].str.strip() == email]
print(colaborador)

def quantidadeHorasExtras(colaborador):
    