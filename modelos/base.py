"""Contrato de um modelo de vídeo, com os valores padrão.

Um modelo define o formato: títulos, contador, abertura, tela final e regras do roteiro.
O estilo (render, filtro VHS, OSD, legendas, áudio e narração) fica no engine.
Cada função recebe tl, o timeline do vídeo, para ler SHOTS, START e o resto.
Este arquivo roda também dentro do Blender, então não pode importar PIL nem scipy.
"""
FPS_SRC = 15
FPS_OUT = 30
END_TEXT = ''
LOOK = 'vhs'        # filtro da imagem: vhs, cctv, broadcast, webcam ou probe
REC_DOT = True      # luz vermelha de gravação piscando no OSD


def timing(shots, end_card=0.0):
    """Devolve TOTAL, START e o início da tela final, que dura end_card segundos."""
    start = {}
    t = 0.0
    for s in shots:
        start[s[0]] = t
        t += s[1]
    return t, start, t - end_card


def bounded(shots, end_card, lo, hi, modelo):
    """Como timing, mas recusa vídeo fora da duração do modelo."""
    total, start, end = timing(shots, end_card)
    if not lo <= total <= hi:
        raise ValueError(f'O vídeo tem {total:.2f}s, e o modelo {modelo} pede de {lo} a {hi}s')
    return total, start, end


def shot_of(tl, t):
    """Take que está na tela no tempo global t."""
    cur = tl.SHOTS[0][0]
    for name, _, _ in tl.SHOTS:
        if tl.START[name] <= t:
            cur = name
    return cur


def rec_label(tl, shot):
    """Texto ao lado da luz de gravação. None não mostra nada."""
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


# ---- takes desenhados ----
# Um take desenhado não passa pelo Blender: o post desenha a imagem dele em 2D, frame a frame.
# Serve para telas de texto, cartelas, mapas e gráficos. O código de desenho usa PIL, então só é
# importado dentro das funções abaixo, que nunca rodam no Blender.

def drawn(tl, shot):
    """Se o take é desenhado em 2D. O padrão são os takes em DRAWN do timeline."""
    return shot in getattr(tl, 'DRAWN', ())


def _cards():
    import importlib, importlib.util
    return importlib.import_module('cards') if importlib.util.find_spec('cards') else None


def card(tl, shot, rt):
    """Imagem 960x720 de um take desenhado: draw_<take>(rt) do cards.py do vídeo."""
    return getattr(_cards(), 'draw_' + shot)(rt)


def paint(tl, shot, rt, img):
    """Desenha por cima do take, depois da cor e antes do OSD: paint_<take>(img, rt) do cards.py do vídeo."""
    fn = getattr(_cards(), 'paint_' + shot, None)
    return fn(img, rt) if fn else img
