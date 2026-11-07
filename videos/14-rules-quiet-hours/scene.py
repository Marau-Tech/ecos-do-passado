"""Ilustrações do filme da biblioteca: o corredor entre as estantes, a mesa de leitura e a silhueta no fim."""
from lib import *
import timeline as TL

SHOTS = {s[0]: s[1] for s in TL.SHOTS if not TL.MODELO.drawn(TL, s[0])}
HOLD_STATES = True

BOOKS = [(0.45, 0.12, 0.1), (0.15, 0.2, 0.25), (0.5, 0.3, 0.12), (0.28, 0.2, 0.1), (0.55, 0.45, 0.3), (0.2, 0.28, 0.2)]


def shelf_row(x, facing, length=9.0, y0=-4.5):
    """Estante comprida em x, com os livros virados para o corredor (facing = +1 olha para +x)."""
    wood = simple('shelfwood', (0.2, 0.12, 0.07), 0.6)
    box('back', (0.05, length, 2.3), (x - facing * 0.3, y0 + length / 2, 1.15), wood)
    mats = [simple(f'book{i}', c, 0.8) for i, c in enumerate(BOOKS)]
    rs_ = np.random.RandomState(int(x * 10) % 97)
    for z in (0.05, 0.5, 0.95, 1.4, 1.85):
        box('board', (0.6, length, 0.05), (x, y0 + length / 2, z), wood)
        y = y0 + 0.1
        while y < y0 + length - 0.3:
            w = rs_.uniform(0.25, 0.6); h = rs_.uniform(0.28, 0.4)
            box('books', (0.22, w, h), (x - facing * 0.08, y + w / 2, z + h / 2 + 0.03), mats[rs_.randint(len(mats))])
            y += w + 0.02
    box('endcap', (0.6, 0.05, 2.3), (x, y0, 1.15), wood)


def hall(far_light=True):
    """Corredor entre duas estantes, com a mesa da bibliotecária e o abajur no fundo. Devolve (luz do fundo, cadeira)."""
    reset(48); world_flat((0.02, 0.018, 0.015), 0.5)
    box('floor', (6, 12, 0.1), (0, 1.5, -0.05), simple('parquet', (0.28, 0.17, 0.09), 0.45))
    box('ceil', (6, 12, 0.1), (0, 1.5, 2.6), simple('ceilm', (0.6, 0.58, 0.5), 0.9))
    wall = simple('wall', (0.55, 0.5, 0.4), 0.9)
    box('wallB', (6, 0.1, 2.6), (0, 6, 1.3), wall)
    box('wallF', (6, 0.1, 2.6), (0, -4.6, 1.3), wall)
    shelf_row(-1.4, 1); shelf_row(1.4, -1)
    wood = simple('deskwood', (0.3, 0.17, 0.08), 0.5)
    box('desk', (1.6, 0.8, 0.08), (0, 4.8, 0.85), wood)
    box('deskbody', (1.5, 0.7, 0.8), (0, 4.8, 0.4), wood)
    chair = bpy.data.objects.new('deskchair', None); link(chair); chair.location = (0, 5.5, 0)
    dark = simple('chairm', (0.08, 0.06, 0.05), 0.6)
    for o in (box('cseat', (0.5, 0.5, 0.08), (0, 0, 0.48), dark), box('cback', (0.5, 0.06, 0.6), (0, 0.25, 0.8), dark)):
        o.parent = chair
    box('lampbase', (0.1, 0.1, 0.35), (0.5, 4.9, 1.05), simple('brass', (0.8, 0.6, 0.25), 0.3, 0.9))
    box('lampshade', (0.35, 0.35, 0.22), (0.5, 4.9, 1.3), emission('shade', (1.0, 0.8, 0.45), 3.0))
    far = point((0.5, 4.6, 1.5), 120.0, (1.0, 0.78, 0.45), 0.2)
    for y in (-2.0, 1.0):
        box('fixture', (0.5, 0.5, 0.05), (0, y, 2.55), emission('fixture', (1.0, 0.9, 0.7), 2.5))
        point((0, y, 2.3), 140.0, (1.0, 0.88, 0.65), 0.4)
    camera((0.0, -4.2, 1.4), (0.0, 4.0, 1.25), 28)
    return far, chair


def still():
    def upd(t, u):
        return ('still',)
    return upd


def build_r1a():
    hall()
    return still()


def build_r3a():
    """Mesa de leitura: três cadeiras de frente para a porta e uma de costas."""
    reset(48); world_flat((0.02, 0.018, 0.015), 0.5)
    wall = simple('wall', (0.55, 0.5, 0.4), 0.9)
    box('floor', (9, 9, 0.1), (0, 0, -0.05), simple('parquet', (0.28, 0.17, 0.09), 0.45))
    box('ceil', (9, 9, 0.1), (0, 0, 2.6), simple('ceilm', (0.6, 0.58, 0.5), 0.9))
    box('wallB', (9, 0.1, 2.6), (0, 4, 1.3), wall); box('wallF', (9, 0.1, 2.6), (0, -4.5, 1.3), wall)
    box('wallL', (0.1, 9, 2.6), (-4.5, 0, 1.3), wall)
    box('door', (1.1, 0.06, 2.1), (0, 3.93, 1.05), emission('hall', (0.45, 0.6, 0.8), 1.2))
    box('frame', (1.3, 0.04, 2.3), (0, 3.95, 1.1), simple('doorframe', (0.2, 0.12, 0.07), 0.6))
    wood = simple('tablewood', (0.3, 0.17, 0.08), 0.5)
    box('table', (2.6, 1.1, 0.06), (0, 0, 0.75), wood)
    for dx in (-1.2, 1.2):
        for dy in (-0.45, 0.45):
            box('leg', (0.06, 0.06, 0.72), (dx, dy, 0.36), wood)
    dark = simple('chairm', (0.08, 0.06, 0.05), 0.6)
    def chair(x, y, face):
        box('cseat', (0.5, 0.5, 0.06), (x, y, 0.46), dark)
        box('cback', (0.5, 0.06, 0.55), (x, y - face * 0.25, 0.76), dark)
        for dx in (-0.2, 0.2):
            for dy in (-0.2, 0.2):
                box('cleg', (0.04, 0.04, 0.44), (x + dx, y + dy, 0.22), dark)
    for x in (-0.8, 0.0, 0.8):
        chair(x, -0.95, 1)
    chair(0.0, 0.95, -1)
    box('lamp', (0.3, 0.3, 0.2), (-0.9, 0.2, 1.0), emission('lampm', (1.0, 0.8, 0.45), 3.0))
    box('book', (0.3, 0.22, 0.04), (0.5, 0.1, 0.8), simple('bk', (0.4, 0.1, 0.1), 0.8))
    point((-0.9, 0.2, 1.2), 90.0, (1.0, 0.8, 0.5), 0.2)
    point((0, 0, 2.3), 100.0, (1.0, 0.88, 0.65), 0.4)
    camera((4.0, -3.4, 2.1), (0.0, 0.4, 0.7), 28)
    return still()


def build_r5a():
    """O corredor vazio: a luz do fundo pisca uma vez."""
    far, chair = hall()
    def upd(t, u):
        off = TL.FLICKER <= t < TL.FLICKER + 0.35
        far.data.energy = 3.0 if off else 120.0
        return off
    return upd


def build_r6a():
    """O mesmo corredor; no fim, uma silhueta alta onde ficava a bibliotecária."""
    far, chair = hall()
    chair.rotation_euler.z = math.radians(200)
    fig = figure((0.0, 5.0, 0.0), 0.0, 1.15, eyes=True)
    def upd(t, u):
        here = t >= TL.SHAPE
        for o in [fig] + list(fig.children_recursive):
            o.hide_render = not here
        return here
    return upd
