# (take, duração, legendas [(início, fim, texto)])
from modelos import rules as MODELO
from modelos.rules import *

SHOTS = [
 ('slate', 4.5, []),
 ('r1', 2.5, [(0.2, 2.5, 'Rule one.')]),
 ('r1a', 6.0, [(0.2, 2.8, 'Keep your voice low.'), (2.8, 6.0, 'The library is a place of quiet.')]),
 ('r2', 2.5, [(0.2, 2.5, 'Rule two.')]),
 ('r2a', 6.0, [(0.2, 3.0, 'Every book is lent, never given.'), (3.0, 6.0, 'Return it by the date stamped inside.')]),
 ('r3', 2.5, [(0.2, 2.5, 'Rule three.')]),
 ('r3a', 6.5, [(0.2, 3.2, 'Choose a seat facing the door.'), (3.2, 6.5, 'Always know who comes in.')]),
 ('r4', 2.5, [(0.2, 2.5, 'Rule four.')]),
 ('r4a', 5.5, [(0.2, 3.0, 'If a book knows your name,'), (3.0, 5.5, 'do not open it.')]),
 ('r5', 2.5, [(0.2, 2.5, 'Rule five.')]),
 ('r5a', 4.5, [(0.3, 3.8, 'Do not answer the shelves.')]),
 ('r6', 2.5, [(0.2, 2.5, 'Rule six.')]),
 ('r6a', 9.0, [(0.3, 3.4, 'Now speak. Loudly.'), (3.4, 7.6, 'It has heard your silence since rule one.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)
DRAWN = ['r2a', 'r4a']
END_TEXT = 'SHHH.'

FILM = ('WESTFIELD PUBLIC LIBRARY', 'PATRON ORIENTATION No. 4', 'QUIET HOURS')
# a barra diz "OF 5", mas a sexta regra aparece inteira
RULES = [('KEEP YOUR VOICE LOW',), ('RETURN BOOKS ON TIME', 'eye'), ('SIT FACING THE DOOR',),
         ('IF A BOOK KNOWS YOUR NAME',), ('DO NOT ANSWER',), ('NOW SPEAK',)]
RULES_OF = 5
FLICKER = 2.0                   # r5a: a luz do fundo apaga e volta
SHAPE = 3.4                     # r6a: uma silhueta aparece no fim do corredor
CLOCK_STOP = START['r6a']       # o relógio da parede para na virada

EVENTS = [(START[f'r{k}'], 0.4, 0.15) for k in range(1, 7)]
EVENTS += [(START['r5a'] + FLICKER, 0.3, 0.12),
           (START['r6a'] + 0.1, 0.8, 0.3),                # a virada
           (START['r6a'] + SHAPE, 0.9, 0.2),
           (END_CARD - 0.2, 0.8, 0.3)]
SUBLIM = []
SUBLIM_GRADE = 'scene'

VOICE = {'voice': 'bm_george', 'lang': 'en-gb', 'speed': 0.92}

GRADE = {'scene': (0.85, 0.96, (1.05, 1.0, 0.9), 0.04)}

def frame_fx(a, shot, rt):
    return a
