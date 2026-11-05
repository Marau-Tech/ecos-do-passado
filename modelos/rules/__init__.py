"""Modelo filme de segurança: uma fita educativa dos anos 80 com regras numeradas, e a última contradiz a primeira.

Regras do roteiro em modelos/rules/GUIA.md.
"""
import re
from modelos.base import *
from modelos.base import drawn as _drawn, card as _card

__all__ = ['FPS_SRC', 'FPS_OUT', 'END_SECS', 'END_TEXT', 'END_TONE', 'MIN_SECS', 'MAX_SECS', 'SLATE_COUNT', 'timing']

MIN_SECS, MAX_SECS = 40, 80
END_SECS = 1.2
END_TEXT = 'BE SAFE.'
END_TONE = False                # tela final sem o tom de alerta do EAS
SLATE_COUNT = 0.8               # segundos de cada número da contagem do filme
_CARD = re.compile(r'r(\d)$')


def timing(shots, end_card=None):
    return bounded(shots, END_SECS if end_card is None else end_card, MIN_SECS, MAX_SECS, 'rules')


def rule_of(shot):
    """Número da regra do take (r3, r3a e r3b são da regra 3), ou None."""
    m = re.match(r'r(\d)', shot)
    return int(m.group(1)) if m else None


def rec_label(tl, shot):
    return 'PLAY'


def title(tl, shot):
    k = rule_of(shot)
    if k is None:
        return None
    return f'RULE {k} OF {len(tl.RULES)}', tl.RULES[k - 1][0]


def opens_section(tl, shot):
    return bool(_CARD.match(shot))


def big_caption(tl, shot):
    return shot == 'slate'


def grade_key(tl, shot):
    k = rule_of(shot)
    return f'r{k}' if k and f'r{k}' in tl.GRADE else 'scene'


def scene_module(tl, shot):
    return 'scene'


def drawn(tl, shot):
    return shot == 'slate' or bool(_CARD.match(shot)) or _drawn(tl, shot)


def card(tl, shot, rt):
    from modelos.rules import draw
    if shot == 'slate':
        return draw.slate(tl, rt)
    if _CARD.match(shot):
        return draw.rule_card(tl, rule_of(shot), rt)
    return _card(tl, shot, rt)
