# agente.py

from router import identificar_intencao, dispatcher


def responder(pergunta: str, df_usuario):
    """Interpreta a pergunta, roteia e executa a função correspondente."""
    intencao, parametros = identificar_intencao(pergunta)
    if intencao and intencao in dispatcher:
        funcao = dispatcher[intencao]
        try:
            resultado = funcao(df_usuario, **parametros)
            return f"✅ Resultado: {resultado}"
        except Exception as e:
            return f"⚠️ Erro ao executar a função: {str(e)}"
    return "🤖 Desculpe, não entendi como responder a essa pergunta."
