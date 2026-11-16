# (take, duração, legendas [(início, fim, texto)])
from modelos import pov as MODELO
from modelos.pov import *

SHOTS = [
    ('intro', 15.0, [
        (0.4, 7.0, 'Sarajevo. Manhã de 28 de junho de 1914.'),
        (7.5, 15.0, 'A cidade desperta para um dia de cerimônia.')
    ]),
    ('t1', 15.0, [
        (0.4, 7.0, 'Há movimento nas ruas próximas ao rio.'),
        (7.5, 15.0, 'A multidão aguarda a passagem do cortejo.')
    ]),
    ('t2', 15.0, [
        (0.4, 7.0, 'Os automóveis se aproximam pela avenida.'),
        (7.5, 15.0, 'No terceiro carro estão Franz Ferdinand e Sophie.')
    ]),
    ('t3', 15.0, [
        (0.4, 7.0, 'O cortejo segue pela Appel Quay.'),
        (7.5, 15.0, 'O rio Miljacka acompanha o caminho.')
    ]),
    ('t4', 15.0, [
        (0.4, 7.0, 'Um homem lança uma bomba contra o automóvel.'),
        (7.5, 15.0, 'Ela atinge o carro e explode sob o veículo seguinte.')
    ]),
    ('t5', 15.0, [
        (0.4, 7.0, 'A explosão espalha pânico pela avenida.'),
        (7.5, 15.0, 'Há feridos entre os ocupantes e os espectadores.')
    ]),
    ('t6', 15.0, [
        (0.4, 7.0, 'Apesar do atentado, o cortejo continua.'),
        (7.5, 15.0, 'Os automóveis seguem até a Prefeitura.')
    ]),
    ('t7', 15.0, [
        (0.4, 7.0, 'Na Prefeitura, acontece a recepção oficial.'),
        (7.5, 15.0, 'A tensão do lado de fora ainda permanece.')
    ]),
    ('t8', 15.0, [
        (0.4, 7.0, 'O arquiduque decide visitar os feridos.'),
        (7.5, 15.0, 'Às 10h45, o casal deixa a Prefeitura.')
    ]),
    ('t9', 15.0, [
        (0.4, 7.0, 'O trajeto de retorno passa pela avenida.'),
        (7.5, 15.0, 'Perto da Ponte Latina, o carro vira na rua errada.')
    ]),
    ('t10', 15.0, [
        (0.4, 7.0, 'O automóvel para para corrigir o caminho.'),
        (7.5, 15.0, 'Gavrilo Princip se aproxima e dispara duas vezes.')
    ]),
    ('t11', 15.0, [
        (0.4, 7.0, 'A multidão reage aos disparos.'),
        (7.5, 15.0, 'Franz Ferdinand e Sophie estão mortalmente feridos.')
    ]),
]

TOTAL, START, END_CARD = timing(
    SHOTS,
    min_secs=175,
    max_secs=180
)

PLACE, DATE = 'SARAJEVO', '28 DE JUNHO DE 1914'
STAMP = '28 JUN 1914'

# Horários aproximados para orientar a narrativa.
# Os marcos históricos mais importantes são indicados nas legendas.
CLOCK = {
    'intro': 9 * 3600 + 55 * 60,
    't1':    10 * 3600,
    't2':    10 * 3600 + 5 * 60,
    't3':    10 * 3600 + 8 * 60,
    't4':    10 * 3600 + 10 * 60,
    't5':    10 * 3600 + 12 * 60,
    't6':    10 * 3600 + 20 * 60,
    't7':    10 * 3600 + 30 * 60,
    't8':    10 * 3600 + 45 * 60,
    't9':    10 * 3600 + 50 * 60,
    't10':   10 * 3600 + 55 * 60,
    't11':   10 * 3600 + 56 * 60,
}

SCENE_OF = {
    'intro': 'rua',
    't1': 'rua',
    't2': 'cortejo',
    't3': 'cortejo',
    't4': 'cortejo',
    't5': 'cortejo',
    't6': 'prefeitura',
    't7': 'prefeitura',
    't8': 'prefeitura',
    't9': 'ponte',
    't10': 'ponte',
    't11': 'ponte',
}

EVENTS = base_events(SHOTS, START)
EVENTS += [(END_CARD - 0.25, 1.0, 0.3)]

SUBLIM = []
SUBLIM_GRADE = 'intro'

VOICE = {'voice': 'pm_alex', 'lang': 'pt-br', 'speed': 1.0}

GRADE = {
    'intro': (0.85, 1.05, (1.02, 1.00, 0.96), 0.02),
    't1':    (0.90, 1.05, (1.02, 1.00, 0.96), 0.02),
    't2':    (0.95, 1.08, (1.02, 1.00, 0.96), 0.02),
    't3':    (0.95, 1.08, (1.02, 1.00, 0.96), 0.02),
    't4':    (0.90, 1.10, (1.04, 0.98, 0.94), 0.02),
    't5':    (0.85, 1.08, (1.02, 0.99, 0.96), 0.02),
    't6':    (0.95, 1.05, (1.02, 1.00, 0.96), 0.02),
    't7':    (0.95, 1.05, (1.02, 1.00, 0.96), 0.02),
    't8':    (0.95, 1.05, (1.02, 1.00, 0.96), 0.02),
    't9':    (0.90, 1.08, (1.02, 0.99, 0.96), 0.02),
    't10':   (0.85, 1.10, (1.02, 0.98, 0.94), 0.02),
    't11':   (0.80, 1.08, (1.02, 0.99, 0.96), 0.02),
}


def frame_fx(a, shot, rt):
    """Efeito extra por frame; a é float RGB 0..1."""
    return a
