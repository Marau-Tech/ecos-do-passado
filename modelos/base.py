"""Contrato de um modelo de vídeo, com os valores padrão.

Um modelo define o formato: títulos, contador, abertura, tela final e regras do roteiro.
O estilo (render, filtro VHS, OSD, legendas, áudio e narração) fica no engine.
Cada função recebe tl, o timeline do vídeo, para ler SHOTS, START e o resto.
Este arquivo roda também dentro do Blender, então não pode importar PIL nem scipy.
"""
FPS_SRC = 15
FPS_OUT = 30
END_TEXT = ''
LOOK = 'vhs'        # filtro da imagem: vhs ou cctv


def timing(shots, end_card=0.0):
    """Devolve TOTAL, START e o início da tela final, que dura end_card segundos."""
    start = {}
    t = 0.0
    for s in shots:
        start[s[0]] = t
        t += s[1]
    return t, start, t - end_card


def rec_label(tl, shot):
    """Texto ao lado da luz de gravação."""
    return 'REC'


def counter(tl, t):
    """Texto do canto superior direito do OSD. None não mostra nada."""
    return None


def footer(tl, shot, t, frame):
    """Texto do canto inferior esquerdo do OSD. None não mostra nada."""
    return f'SP  {int(t) // 60}:{int(t) % 60:02d}:{frame % 30:02d}'


def title(tl, shot):
    """(título, subtítulo) da barra de cima. None deixa a barra vazia."""
    return None


def opens_section(tl, shot):
    """Se este take abre um trecho. No modo 4:3 o título só aparece nele."""
    return False


def big_caption(tl, shot):
    """Se a legenda deste take vai grande, na barra de cima."""
    return False


def labels(tl, shot):
    """Rótulos em cima da imagem: [((x, y), texto)]."""
    return ()


def grade_key(tl, shot):
    """Chave de GRADE usada neste take."""
    return shot


def scene_module(tl, shot):
    """Arquivo de videos/<video>/ que tem build_<take>()."""
    return shot
