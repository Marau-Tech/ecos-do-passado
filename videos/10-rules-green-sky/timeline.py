# (take, duração, legendas [(início, fim, texto)])
from modelos import rules as MODELO
from modelos.rules import *

SHOTS = [
 ('slate', 4.5, []),
 ('r1', 2.5, [(0.2, 2.5, 'Rule one.')]),
 ('r1a', 6.0, [(0.2, 6.0, 'If the sky turns green, go inside and stay there.')]),
 ('r2', 2.5, [(0.2, 2.5, 'Rule two.')]),
 ('r2a', 5.0, [(0.2, 5.0, 'Listen for the all-clear signal.')]),
 ('r3', 2.5, [(0.2, 2.5, 'Rule three.')]),
 ('r3a', 6.5, [(0.2, 3.2, 'Your house has the same windows as always.'), (3.2, 6.5, 'Do not count them.')]),
 ('r4', 2.5, [(0.2, 2.5, 'Rule four.')]),
 ('r4a', 6.5, [(0.2, 3.4, 'Family members have keys.'), (3.4, 6.5, 'Wait until the knocking stops.')]),
 ('r5', 2.5, [(0.2, 2.5, 'Rule five.')]),
 ('r5a', 9.2, [(0.4, 4.0, 'If you can see the green sky,'), (4.0, 7.8, 'you are not inside.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)

FILM = ('THE DEPARTMENT OF CIVIL READINESS', 'SAFETY FILM No. 12', 'WHEN THE SKY TURNS GREEN')
# a sexta regra só aparece num frame (SUBLIM); a barra diz "OF 6" desde o começo
RULES = [('STAY INSIDE AFTER DARK', 'moon'), ('KEEP A RADIO NEARBY',), ('DO NOT COUNT THE WINDOWS', 'eye'),
         ('IF SOMEONE KNOCKS, WAIT',), ('THE SKY IS NOT OUTSIDE',), ('LET THEM IN',)]
EXTRA_WINDOW = 4.6              # no r3a, uma janela a mais acende
KNOCKS = (1.0, 1.45, 1.9, 4.4, 4.85, 5.3)   # batidas na porta, dentro do r4a

# glitch: (tempo global, força, duração)
EVENTS = [(START[f'r{k}'], 0.4, 0.15) for k in range(1, 6)]
EVENTS += [(START['r3a'] + EXTRA_WINDOW, 0.3, 0.12),
           (START['r5a'] + 4.0, 0.8, 0.3),          # a virada
           (START['r5a'] + 7.5, 0.9, 0.2),          # logo depois da regra 6, para ela ficar legível na pausa
           (END_CARD - 0.2, 0.8, 0.3)]
# quadro subliminar: a cartela da regra 6
SUBLIM = [(START['r5a'] + 7.4, 'r6', 0)]          # longe do glitch da tela final, que começa em END_CARD - 0.2
SUBLIM_GRADE = 'scene'

VOICE = {'voice': 'bm_lewis', 'lang': 'en-gb', 'speed': 0.92}

GRADE = {'scene': (0.85, 0.96, (1.05, 1.0, 0.9), 0.04)}  # filme dos anos 80: quente e lavado

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
