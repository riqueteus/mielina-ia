"""Laudos fictícios (mocks) de ressonância magnética com dados sensíveis.

Cada laudo simula um formato real de cabeçalho/corpo de laudo e traz dados
pessoais inventados (nome, CPF, RG, telefone, e-mail, nascimento, prontuário)
que não podem aparecer no texto anonimizado.
"""

MOCKS = {
    "laudo_rm_encefalo": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Paciente: Maria Joaquina da Silva
Data de Nascimento: 23/04/1981
CPF: 391.847.562-08
RG: 45.678.901-2
Telefone: (11) 98765-4321
E-mail: maria.joaquina.silva@email.com.br
Prontuário: 123456
Solicitante: Dra. Ana Beatriz Carvalho
Data: 14/07/2026

Indicação clínica: investigação diagnóstica de esclerose múltipla em paciente com episódios de neurite óptica recorrente.

Técnica: sequências sagitais e axiais em T1, T2 e FLAIR, além de DWI/ADC.

Achados: presença de múltiplas lesões desmielinizantes em região periventricular, bilateral, algumas com aspecto ovalado, orientadas perpendicularmente ao corpo caloso. Observam-se também focos de hipersinal em T2/FLAIR na região justacortical dos lobos frontais. Não há lesões em fossa posterior. Não foram identificadas lesões com realce após a administração de contraste.

Conclusão: exame sugestivo de doença desmielinizante com disseminação no espaço. Recomendado controle evolutivo.
""",
        "nomes": ["Maria Joaquina da Silva", "Ana Beatriz Carvalho"],
        "cpf": "391.847.562-08",
        "rg": "45.678.901-2",
        "telefone": "(11) 98765-4321",
        "email": "maria.joaquina.silva@email.com.br",
        "nascimento": "23/04/1981",
        "prontuario": "123456",
        "data_exame": "14/07/2026",
        "termos_medicos": ["esclerose", "periventricular", "desmielinizante"],
    },
    "laudo_rm_coluna_cervical": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DA COLUNA CERVICAL

Nome: Pedro Henrique Alves Santos Prontuário: 2026070234
Data de Nascimento: 05/11/1975
CPF: 088.129.547-33
RG: 12.345.678-9
Telefone: (21) 97654-2109
E-mail: pedro.henrique.santos@email.com.br
Solicitante: Dr. Ricardo Almeida Fonseca Data: 02/08/2026

Indicação clínica: controle de doença desmielinizante previamente diagnosticada.

Técnica: sequências sagitais T1 e T2, axiais T2 e STIR.

Achados: identificada lesão de hipersinal em T2 na medula espinhal ao nível de C5/C6, medindo aproximadamente 8 mm no maior eixo, sem realce pós-contraste. Não há outras lesões medulares. Canal vertebral com dimensões preservadas.

Conclusão: lesão medular única compatível com placa de desmielinização.
""",
        "nomes": ["Pedro Henrique Alves Santos", "Ricardo Almeida Fonseca"],
        "cpf": "088.129.547-33",
        "rg": "12.345.678-9",
        "telefone": "(21) 97654-2109",
        "email": "pedro.henrique.santos@email.com.br",
        "nascimento": "05/11/1975",
        "prontuario": "2026070234",
        "data_exame": "02/08/2026",
        "termos_medicos": ["medula espinhal", "C5/C6", "desmielinização"],
    },
    "laudo_rm_encefalo_com_contraste": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO CRÂNIO COM CONTRASTE

Paciente: Juliana Cristina Ferreira Braga
Data de Nascimento: 17/09/1990
CPF: 567.098.213-41
RG: 33.876.112-0
Telefone: (31) 98877-1122
E-mail: juliana.braga@email.com
Prontuário: 789012
Solicitante: Dra. Camila Rodrigues Pereira
Data: 29/07/2026

Indicação clínica: monitoramento de tratamento com imunomodulador.

Técnica: sequências axiais T1, T2 e FLAIR, DWI/ADC e estudo pós-contraste com gadolínio.

Achados: múltiplas lesões desmielinizantes periventriculares e justacorticais, com duas lesões apresentando realce anelar após o contraste, sugestivas de atividade inflamatória. Observa-se ainda uma lesão na fossa posterior, no pedúnculo cerebelar médio esquerdo, medindo 6 mm.

Conclusão: evidência de atividade inflamatória da doença. Sinais de progressão em relação ao exame anterior.
""",
        "nomes": ["Juliana Cristina Ferreira Braga", "Camila Rodrigues Pereira"],
        "cpf": "567.098.213-41",
        "rg": "33.876.112-0",
        "telefone": "(31) 98877-1122",
        "email": "juliana.braga@email.com",
        "nascimento": "17/09/1990",
        "prontuario": "789012",
        "data_exame": "29/07/2026",
        "termos_medicos": ["realce", "gadolínio", "periventriculares", "atividade inflamatória"],
    },
    "laudo_rm_encefalo_e_coluna": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO ENCÉFALO E COLUNA CERVICAL

PACIENTE: CARLOS EDUARDO MENEZES
DATA DE NASCIMENTO: 12/07/1978
CPF: 312.456.789-01
RG: 22.333.444-5
TELEFONE: (11) 97711-3344
EMAIL: carlos.menezes@email.com
AN: 2026091847
SOLICITANTE: DR. FELIPE AUGUSTO NUNES
DATA: 21/08/2026

Indicação clínica: acompanhamento de esclerose múltipla com suspeita de atividade.

Técnica: sequências T1, T2 e FLAIR no encéfalo e sagitais na coluna cervical.

Achados: lesões periventriculares e justacorticais típicas de desmielinização, sem realce. Ausência de lesões medulares.

Impressão: doença desmielinizante sem sinais de atividade inflamatória.
""",
        "nomes": ["CARLOS EDUARDO MENEZES", "FELIPE AUGUSTO NUNES"],
        "cpf": "312.456.789-01",
        "rg": "22.333.444-5",
        "telefone": "(11) 97711-3344",
        "email": "carlos.menezes@email.com",
        "nascimento": "12/07/1978",
        "prontuario": "2026091847",
        "data_exame": "21/08/2026",
        "termos_medicos": ["esclerose", "periventricular", "justacorticais", "desmielinização"],
    },
    "laudo_rm_coluna_toracica": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DA COLUNA TORÁCICA

Nome: Roberto Carlos Pereira Lima Prontuário: 998877
Data de Nascimento: 03/02/1985
CPF: 19876543210
RG: 44.567.890-1
Telefone: 11981234567
E-mail: roberto.pereira@email.com.br
Solicitante: Dra. Márcia Helena Costa Data: 09/09/2026

Estudo da coluna torácica com sequências sagitais T1, T2 e STIR. Identificada lesão medular ao nível de T7/T8 com discreto hipersinal em T2, medindo cerca de 1,2 cm, sem realce pós-contraste. Demais níveis vertebrais preservados.
""",
        "nomes": ["Roberto Carlos Pereira Lima", "Márcia Helena Costa"],
        "cpf": "19876543210",
        "rg": "44.567.890-1",
        "telefone": "11981234567",
        "email": "roberto.pereira@email.com.br",
        "nascimento": "03/02/1985",
        "prontuario": "998877",
        "data_exame": "09/09/2026",
        "termos_medicos": ["medular", "T7/T8", "STIR"],
    },
    "laudo_rm_orbitas": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DAS ÓRBITAS

Paciente: Beatriz Oliveira Rocha
Data de Nascimento: 01/12/1995
CPF: 700.123.456-78
RG: 11.222.333-4
Telefone: (31) 99874-5566
E-mail: beatriz.rocha@email.com
Prontuário: 445566
Médico executante: Dr. Paulo Sérgio Andrade
Solicitante: Dr. Marco Túlio Braga
Data: 30/06/2026

Sem sinais de neurite óptica. Nervos ópticos com calibre e sinal preservados, simétricos.
""",
        "nomes": ["Beatriz Oliveira Rocha", "Paulo Sérgio Andrade", "Marco Túlio Braga"],
        "cpf": "700.123.456-78",
        "rg": "11.222.333-4",
        "telefone": "(31) 99874-5566",
        "email": "beatriz.rocha@email.com",
        "nascimento": "01/12/1995",
        "prontuario": "445566",
        "data_exame": "30/06/2026",
        "termos_medicos": ["neurite óptica", "nervos ópticos"],
    },
    "laudo_rm_encefalo_prosa": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Nome: João Vítor Almeida Prontuário: 778899
Data de Nascimento: 18/08/1988
CPF: 423.789.123-56
RG: 55.666.777-8
Telefone: (11) 98123-4455
E-mail: joao.vitor.almeida@email.com
Solicitante: Dra. Fernanda Lima Rocha Data: 12/05/2026

Exame de controle de doença desmielinizante. Presença de poucas lesões em T2/FLAIR na região periventricular, sem realce após contraste. O paciente João Vítor Almeida apresenta quadro estável.
""",
        "nomes": ["João Vítor Almeida", "Fernanda Lima Rocha"],
        "cpf": "423.789.123-56",
        "rg": "55.666.777-8",
        "telefone": "(11) 98123-4455",
        "email": "joao.vitor.almeida@email.com",
        "nascimento": "18/08/1988",
        "prontuario": "778899",
        "data_exame": "12/05/2026",
        "termos_medicos": ["desmielinizante", "periventricular", "T2/FLAIR"],
    },
    "laudo_rm_coluna_lombar": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DA COLUNA LOMBAR

Paciente: Sandra Regina Martins
Data de Nascimento: 27/04/1970
CPF: 289.123.654-90
RG: 88.999.000-1
Telefone: (41) 98844-2233
E-mail: sandra.martins@email.com.br
Prontuário: 332211
Solicitante: Dr. Antônio Carlos Prado
Data: 18/03/2026

Técnica: sequências sagitais T1 e T2 e axiais T2.

Achados: discreta lesão desmielinizante na medula lombar, no cone medular, sem compressão radicular. Canal de L3 a L5 com leve estenose degenerativa.
""",
        "nomes": ["Sandra Regina Martins", "Antônio Carlos Prado"],
        "cpf": "289.123.654-90",
        "rg": "88.999.000-1",
        "telefone": "(41) 98844-2233",
        "email": "sandra.martins@email.com.br",
        "nascimento": "27/04/1970",
        "prontuario": "332211",
        "data_exame": "18/03/2026",
        "termos_medicos": ["desmielinizante", "cone medular", "estenose"],
    },
    "laudo_rm_encefalo_sem_achados": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Paciente: Larissa Fernanda Cardoso
Data de Nascimento: 09/10/2001
CPF: 154.987.321-76
RG: 66.543.210-0
Telefone: (85) 99911-8877
E-mail: larissa.cardoso@email.com
Prontuário: 908070
Solicitante: Dra. Roberta Vasconcelos
Data: 25/02/2026

Exame sem alterações significativas. Sem lesões desmielinizantes, sem sinais de atrofia. Substância branca e cinzenta sem particularidades.
""",
        "nomes": ["Larissa Fernanda Cardoso", "Roberta Vasconcelos"],
        "cpf": "154.987.321-76",
        "rg": "66.543.210-0",
        "telefone": "(85) 99911-8877",
        "email": "larissa.cardoso@email.com",
        "nascimento": "09/10/2001",
        "prontuario": "908070",
        "data_exame": "25/02/2026",
        "termos_medicos": ["desmielinizantes", "atrofia"],
    },
    "laudo_rm_encefalo_controle": {
        "texto": """\
RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Nome: André Luiz Barbosa Prontuário: 654321
Data de Nascimento: 14/01/1992
CPF: 334.556.778-90
RG: 10.987.654-3
Telefone: (19) 97766-5544
E-mail: andre.barbosa@email.com
Solicitante: Dr. Gustavo Henrique Silva Data: 07/11/2026

Controle evolutivo. Comparado ao exame anterior de 03/05/2026, não há lesões novas nem lesões com realce. Persistem lesões periventriculares estáveis.
""",
        "nomes": ["André Luiz Barbosa", "Gustavo Henrique Silva"],
        "cpf": "334.556.778-90",
        "rg": "10.987.654-3",
        "telefone": "(19) 97766-5544",
        "email": "andre.barbosa@email.com",
        "nascimento": "14/01/1992",
        "prontuario": "654321",
        "data_exame": "07/11/2026",
        "termos_medicos": ["periventriculares", "realce", "controle evolutivo"],
    },
}
