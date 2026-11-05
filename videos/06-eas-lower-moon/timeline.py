# (take, duração, legendas [(início, fim, texto)])
from modelos import eas as MODELO
from modelos.eas import *
import numpy as np

SHOTS = [
 ('pgm', 2.0, []),
 ('tone', 5.5, []),
 ('m1', 6.0, [(0.3, 3.1, 'This is a civil danger warning.'), (3.1, 6.0, 'Remain indoors until sunrise.')]),
 ('m2', 5.5, [(0.3, 2.5, 'Close all curtains.'), (2.5, 5.5, 'Do not look at the moon.')]),
 ('v1', 4.5, []),
 ('m3', 6.0, [(0.3, 2.9, 'If you see two moons,'), (2.9, 6.0, 'the lower one is not the moon.')]),
 ('m4', 6.0, [(0.3, 3.1, 'It is looking for lit windows.'), (3.1, 6.0, 'Turn off all lights now.')]),
 ('v2', 6.0, []),
 ('m5', 9.1, [(0.6, 3.9, 'This station did not send the previous message.'), (3.9, 6.0, 'Leave your lights on.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)

STATION = 'KXLT 58'
CLOCK = 3 * 3600 + 12 * 60
HEADLINE = ('EMERGENCY ALERT', 'CIVIL DANGER WARNING')
TITLES = {'v1': ('LIVE', 'KXLT TOWER CAM'), 'v2': ('LIVE', 'KXLT TOWER CAM')}
EOM_AT = 6.1                    # fim de mensagem, em segundos dentro do m5

CRAWL = 'A CIVIL DANGER WARNING IS IN EFFECT FOR BRIDGEFORD COUNTY UNTIL SUNRISE.   REMAIN INDOORS.'
ALERTS = {
 'pgm': {'style': 'bars', 'lines': ['KXLT 58 · OVERNIGHT']},
 'tone': {'lines': ['CIVIL DANGER WARNING'], 'blink': True},
 'm1': {'lines': ['THE FOLLOWING MESSAGE IS FOR', 'BRIDGEFORD COUNTY'], 'crawl': CRAWL},
 'm2': {'style': 'black', 'head': 'INSTRUCTIONS', 'lines': ['CLOSE ALL CURTAINS', 'DO NOT LOOK AT THE MOON'], 'crawl': CRAWL},
 'm3': {'style': 'blue', 'head': 'INSTRUCTIONS', 'lines': ['IF YOU SEE TWO MOONS', 'THE LOWER ONE IS NOT THE MOON'], 'type': True,
        'crawl': 'MOONSET 4:51 AM.   THE LOWER ONE DOES NOT SET.'},
 'm4': {'style': 'blue', 'head': 'INSTRUCTIONS', 'lines': ['TURN OFF ALL LIGHTS'], 'type': True},
 'm5': {'lines': ['CORRECTION', 'DISREGARD THE PREVIOUS INSTRUCTION'], 'blink': True,
        'crawl': 'DO NOT TURN OFF YOUR LIGHTS.   DO NOT TURN OFF YOUR LIGHTS.'},
}

WINDOWS_OFF = (1.0, 1.9, 2.6, 3.3)      # janelas apagando, em segundos dentro do v2; a quinta fica acesa

# glitch: (tempo global, força, duração)
EVENTS = [(START['tone'] - 0.15, 1.0, 0.45),         # o alerta corta a programação
          (START['v1'], 0.35, 0.15), (START['v2'], 0.35, 0.15),
          (START['v2'] + 5.4, 0.6, 0.25),
          (START['m5'], 1.0, 0.5),                    # a emissora retoma o sinal
          (END_CARD - 0.2, 0.8, 0.3)]
# quadros subliminares: (tempo global, take, frame)
SUBLIM = [(START['m4'] + 4.7, 'v1', 0)]
SUBLIM_GRADE = 'scene'

VOICE = {'voice': 'am_michael', 'lang': 'en-us', 'speed': 0.9, 'fx': 'radio'}

GRADE = {'scene': (0.8, 1.0, (0.94, 0.97, 1.06), 0.0)}  # saturação, contraste, tint RGB, lift

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1. Ganho da câmera noturna."""
    return np.clip(a, 0, 1) ** 0.72
