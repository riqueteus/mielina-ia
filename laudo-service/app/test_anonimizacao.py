from app.services.anonimizador import anonimizar_texto


EXEMPLO = """O estudo de ressonância magnética do crânio realizado com sequências ponderadas em T1, T2 e
FLAIR com cortes sagitais, axiais e coronais antes e após a injeção de contraste paramagnético por
via endovenosa, mostra:

São vistas algumas pequenas áreas focais de hipersinal nas ponderações T2 e FLAIR, caracterizando
desmielinização, localizadas principalmente em região pericalosa, mais expressivas nos lobos parietais.
A maior delas está localizada na região mais posterior do tronco do corpo caloso à esquerda, medindo cerca
de 0,6 cm.

IMPRESSÃO:
Achados compatíveis com esclerose múltipla.
Não há sinais de doença em atividade.

Nome: João José Maria Ana Prontuário: 500309802
Data de Nascimento: 01/01/1990 AN: 0000060000101477
Solicitante: MARIA MADALENA APARECIDA Data: 24/07/2021 17:17:00
RESSONÂNCIA MAGNÉTICA DO CRÂNIO"""


def main():
    print("=== TEXTO ORIGINAL ===")
    print(EXEMPLO)
    print("\n=== TEXTO ANONIMIZADO ===")
    anon = anonimizar_texto(EXEMPLO)
    print(anon)
    print()
    print("=== Datas no texto anonimizado (para cronologia) ===")
    import re

    datas = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", anon)
    print("Datas preservadas:", datas)


if __name__ == "__main__":
    main()