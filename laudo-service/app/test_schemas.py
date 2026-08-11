from datetime import date

from app.schemas import LaudoExtraido, Lesao


exemplo = LaudoExtraido(
    data_exame=date(2021, 7, 24),
    tipo_exame="RM de crânio",
    num_lesoes_total=2,
    lesoes=[
        Lesao(
            localizacao="região pericalosa, tronco do corpo caloso esquerdo",
            regiao="corpo caloso",
            tamanho_mm=6.0,
            caracteristica="hipersinal T2/FLAIR, sem realce",
            realce_contraste=False,
        ),
        Lesao(
            localizacao="regiões periventriculares parietais",
            regiao="periventricular",
            caracteristica="hipersinal T2/FLAIR",
        ),
    ],
    lesoes_periventriculares=1,
    lesoes_novas=0,
    lesoes_com_realce=0,
    lesao_maior_mm=6.0,
    conclusao="Achados compatíveis com esclerose múltipla. Sem sinais de doença em atividade.",
    atividade_doenca="inativa",
    diagnostico_principal="esclerose múltipla",
)


def main():
    print("=== Validação do schema laudo ===")
    print("ID do objeto:", id(exemplo))
    print("Data exame:", exemplo.data_exame)
    print("Nº lesões:", exemplo.num_lesoes_total)
    print("Atividade:", exemplo.atividade_doenca)
    print()

    print("=== Usando model_dump() (dicionário, pronto para JSON) ===")
    dump = exemplo.model_dump()
    print(f"Data exame: {dump['data_exame']}")
    print(f"Primeira lesão: {dump['lesoes'][0]}")
    print()

    print("=== Usando model_validate() (recebe dict / JSON do mundo externo) ===")
    de_json = LaudoExtraido.model_validate(dump)
    print("Validado de volta:", de_json == exemplo)
    print()

    print("=== Campos obrigatórios? (todos opcionais) ===")
    vazio = LaudoExtraido()
    print("Laudo vazio criou sem erro:", vazio.model_dump())


if __name__ == "__main__":
    main()