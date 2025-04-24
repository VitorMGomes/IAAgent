import pandas as pd

#//===================================================================//
# Verifica se o email existe no DF                                    //
#//===================================================================//

def autenticar_usuario(email: str, df_holerite: pd.DataFrame) -> bool:
    return email in df_holerite["Email"].values
