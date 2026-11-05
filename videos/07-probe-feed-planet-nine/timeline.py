# (take, duração, legendas [(início, fim, texto)]): a legenda é o log do operador
from modelos import probe_feed as MODELO
from modelos.probe_feed import *

HEADER = ['DEEP SPACE NETWORK', 'CRAFT     VESPER-2', 'TARGET    PLANET NINE', 'LIGHT     55h 12m', 'RECEIVING IMAGE SEQUENCE']
LOG = REVEAL_AT + REVEAL_SECS + 0.1     # o log aparece depois que a imagem termina de chegar

SHOTS = [
 ('head', 4.5, []),
 ('i1', 6.0, [(LOG, 6.0, 'IMAGE 01 RECEIVED. CHECKSUM OK.')]),
 ('i2', 6.0, [(LOG, 6.0, 'IMAGE 02 RECEIVED. CHECKSUM OK.')]),
 ('i3', 6.0, [(LOG, 6.0, 'IMAGE 03 RECEIVED. CHECKSUM OK.')]),
 ('i4', 6.5, [(LOG, 6.5, 'IMAGE 04 RECEIVED. FEATURE FLAGGED.')]),
 ('i5', 6.5, [(LOG, 6.5, 'OBJECT COUNT: 2,416.')]),
 ('i6', 11.4, [(6.4, 9.4, 'IMAGE 06 WAS NOT TAKEN BY VESPER-2.')]),
]
TOTAL, START, END_CARD = timing(SHOTS)

PROBE = 'VESPER-2'
TARGET = 'PLANET NINE'
SUBTITLES = {'i1': 'ALT 410,000 KM', 'i2': 'ALT 41,000 KM', 'i3': 'ALT 3,200 KM',
             'i4': 'ALT 900 KM', 'i5': 'ALT 60 KM', 'i6': 'SOURCE: SURFACE'}
SIGNAL = (-138.0, -151.0)
REVEAL = {'i6': (0.3, 6.0)}             # a última chega mais devagar

# perda de pacote: (tempo global, força, duração)
EVENTS = [(START['i5'] + LOG - 0.05, 0.45, 0.2),     # as sombras terminam de chegar
          (START['i6'] + 9.0, 1.0, 0.4)]             # o sinal cai
SUBLIM = []
SUBLIM_GRADE = 'img'

GRADE = {'img': (0.0, 1.12, (0.96, 1.0, 0.98), 0.0)}  # preto e branco: filtro CLEAR
GRADE['i6'] = (1.0, 1.12, (0.96, 1.0, 0.98), 0.0)     # i6 tem cor: o resto é cinza, só a Terra é azul

def frame_fx(a, shot, rt):
    """efeito extra por frame; a é float RGB 0..1"""
    return a
