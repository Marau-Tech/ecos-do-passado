# (take, duração, legendas [(início, fim, texto)])
from modelos import pov as MODELO
from modelos.pov import *

SHOTS = [
 ('intro', 5.0, [(0.4, 5.0, 'Stalingrado, novembro de 1942.')]),
 ('t1', 7.0, [(0.3, 3.5, 'Meus pés afundam na neve suja.'), (3.6, 7.0, 'O frio corta o rosto.')]),
 ('t2', 7.0, [(0.3, 3.5, 'Ao longe, a artilharia não para.'), (3.6, 7.0, 'Cada clarão é uma rua a menos.')]),
 ('t3', 7.0, [(0.3, 3.5, 'Encontro abrigo num porão.'), (3.6, 7.0, 'Alguém respira no escuro.')]),
 ('t4', 8.0, [(0.4, 3.8, 'São dos nossos.'), (4.0, 8.0, 'Ninguém fala. Ninguém dorme.')]),
 ('t5', 8.5, [(0.4, 3.5, 'Quando o silêncio volta,'), (3.6, 7.0, 'nada aqui é como antes.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)

PLACE, DATE = 'STALINGRADO', 'NOVEMBRO DE 1942'
STAMP = 'NOV 1942'
CLOCK = {'intro': 15 * 3600 + 40 * 60, 't1': 15 * 3600 + 52 * 60, 't2': 16 * 3600 + 18 * 60,
         't3': 16 * 3600 + 47 * 60, 't4': 23 * 3600 + 5 * 60, 't5': 6 * 3600 + 52 * 60}
SCENE_OF = {'intro': 'rua', 't1': 'rua', 't2': 'rua', 't5': 'rua', 't3': 'porao', 't4': 'porao'}

FLASHES = [0.7, 2.4, 4.0, 5.7]  # clarões no horizonte do t2; o estrondo chega 1,2s depois
BOOM_DELAY = 1.2

EVENTS = base_events(SHOTS, START)
EVENTS += [(START['t2'] + f, 0.25, 0.08) for f in FLASHES]
EVENTS += [(END_CARD - 0.25, 1.0, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'intro'

VOICE = {'voice': 'pm_alex', 'lang': 'pt-br', 'speed': 1.0}

GRADE = {  # saturação, contraste, tint RGB, lift
 'intro': (0.55, 1.08, (0.95, 0.98, 1.05), 0.03),
 't1': (0.55, 1.08, (0.95, 0.98, 1.05), 0.03),
 't2': (0.6, 1.1, (1.02, 0.97, 0.95), 0.03),
 't3': (0.5, 1.12, (0.98, 0.97, 1.0), 0.02),
 't4': (0.65, 1.1, (1.08, 0.98, 0.86), 0.02),
 't5': (0.7, 1.05, (1.08, 0.99, 0.9), 0.04),
}


def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
