"""Personagem POV no Blender: cria as peças, deforma por skinning e acompanha a câmera.

Uso numa cena:

    from pov import create_character
    me = create_character(cam, 'sarajevo_civilian_1914')
    def update(t, u):
        walk_pov(cam, t, ...)
        me.update(t, cam, speed=0.55, heading=0.0, actions=[('watch', 3.0, 8.0)])

O corpo segue a posição da câmera e o rumo da caminhada; não copia o tremor nem a
inclinação da cabeça. O que aparece na tela depende de para onde a câmera olha e do que
as ações fazem com as mãos. update é função pura de t: qualquer frame pode ser renderizado
sozinho, em qualquer ordem.
"""
import math
import bpy
import numpy as np
from mathutils import Matrix
from lib import link
from . import skeleton as S, motion as M, geometry as G, outfits as O, materials as MT
from .fuse import add_fuse


def rest_params():
    arms, legs = {}, {}
    for side, s in (('R', 1), ('L', -1)):
        arms[side] = {'W': S.shoulder0(s) + np.array([0, 0, -(S.UPPER + S.FORE)]), 'F': np.array([0, 0, -1.0]),
                      'D': np.array([s * 1.0, 0, 0]), 'pole': np.array([0, -1.0, 0]),
                      'curls': np.zeros((4, 3)), 'thumb': np.zeros(4), 'raise': 0.0}
        Rf, Rt = S.foot_frames(s, 0.0)
        legs[side] = {'A': np.array([s * 0.09, 0, S.ANKLE_H]), 'Rf': Rf, 'Rt': Rt, 'pole': np.array([0, 1.0, 0])}
    return {'arms': arms, 'legs': legs, 'props': {'rifle': (np.eye(3), np.zeros(3)), 'head': (np.eye(3), S.HEAD_PIVOT.copy())}}


def _materials(cfg, tag):
    c = cfg['colors']
    tq = cfg['torso']
    mats = {
        'skin': MT.skin(f'{tag}_skin', c['skin']),
        'nail': MT.skin_tint(f'{tag}_nail', tuple(min(1.0, c * 1.05 + 0.03) for c in c['skin'])),
        'leather': MT.leather(f'{tag}_leather', c['leather'], cfg.get('leather_rough', 0.45),
                              0.35 if cfg['footwear'] == 'ankle_boot' else 0.0),
        'sole': MT.leather(f'{tag}_sole', c['sole'], 0.8),
        'button': MT.metal(f'{tag}_button', c['button'], 0.5, 0.0 if cfg['footwear'] == 'ankle_boot' or 'quilted' in c else 0.5),
    }
    fab = tq['fabric']
    mats['sleeve'] = MT.fabric(f'{tag}_sleeve', c[fab], quilt=cfg['sleeve'].get('quilt'),
                               rough=0.92 if fab != 'jacket' else 0.86)
    mats['trousers'] = MT.fabric(f'{tag}_trousers', c[cfg['trousers']['fabric']], quilt=cfg['trousers'].get('quilt'),
                                 crease=None)
    if cfg['shirt_cuff']:
        mats['shirt'] = MT.fabric(f'{tag}_shirt', c['shirt'], rough=0.7, sheen=0.25, mottle=0.04, fine=0.1)
    if cfg['gloves']:
        mats['glove'] = MT.knit(f'{tag}_glove', c['glove'])
    if cfg.get('belt'):
        mats['belt'] = MT.leather(f'{tag}_belt', c['belt'], 0.5)
        mats['buckle'] = MT.metal(f'{tag}_buckle', c.get('button', (0.3, 0.3, 0.3)), 0.45, 0.6)
    if cfg.get('rifle'):
        mats['wood'] = MT.wood(f'{tag}_wood', c['wood'])
        mats['steel'] = MT.metal(f'{tag}_steel', c['steel'], 0.32)
    if 'metal' in c:
        mats['watch'] = MT.metal(f'{tag}_watch', c['metal'], 0.18, 1.0)
        mats['watch_face'] = MT.enamel(f'{tag}_watch_face', (0.90, 0.875, 0.80))
        mats['watch_hands'] = MT.metal(f'{tag}_watch_hands', (0.05, 0.05, 0.08), 0.25, 0.9)   # aço azulado
        mats['watch_glass'] = MT.glass(f'{tag}_watch_glass')
    return mats


def _front_seams(tspec, circ):
    """u da abertura da frente: no centro (uma fileira) ou à direita do usuário (duas fileiras)."""
    if tspec['front'] == 'double':
        rx = float(np.mean([s[1] for s in tspec['stations']]))
        return [math.acos(0.085 / rx) / (2 * math.pi) * circ]
    return [circ / 4]


def build_parts(cfg, rest):
    """(cage, chave do material, grupo) de todas as peças. grupo: None (sempre), 'watch', 'rifle'."""
    parts = []
    glove = 0.0025 if cfg['gloves'] else 0.0
    for side, s in (('R', 1), ('L', -1)):
        hcage, nails = G.hand(side, s, rest, glove)
        hcage.merge(G.forearm_skin(side, rest, glove))      # punho contínuo depois da fusão
        hcage.fuse = True
        parts.append((hcage, 'glove' if glove else 'skin', None))
        if nails:
            parts.append((nails, 'nail', None))
        sl, end = G.sleeve(side, s, rest, cfg['sleeve'])
        parts.append((sl, 'sleeve', None))
        if cfg['shirt_cuff']:
            parts.append((G.shirt_cuff(side, rest, end), 'shirt', None))
        if cfg['sleeve'].get('cuff_buttons'):
            b = G.Cage(f'pov_{side}_cuff_buttons')
            G.sleeve_buttons(side, s, rest, end, cfg['sleeve']['cuff_buttons'], b)
            parts.append((b, 'button', None))
        parts.append((G.trousers(side, s, rest, cfg['trousers']), 'trousers', None))
        up, sole, laces = G.footwear(side, s, rest, cfg['footwear'])
        parts.append((up, 'leather', None))
        parts.append((sole, 'sole', None))
        if laces:
            parts.append((laces, 'sole', None))
    tc = G.torso(cfg['torso'])
    parts.append((tc, 'torso', None))
    bt = G.Cage('pov_buttons')
    G.torso_buttons(cfg['torso'], bt)
    parts.append((bt, 'button', None))
    if cfg.get('belt'):
        b, k = G.belt(cfg['torso'], cfg['belt'])
        parts += [(b, 'belt', None), (k, 'buckle', None)]
    if cfg.get('rifle'):
        wood, steel = G.rifle(cfg['rifle'])
        parts += [(wood, 'wood', 'rifle'), (steel, 'steel', 'rifle')]
    if 'metal' in cfg['colors']:
        case, face, hands, glass = G.pocket_watch(rest)
        parts += [(case, 'watch', 'watch'), (face, 'watch_face', 'watch'), (hands, 'watch_hands', 'watch'),
                  (glass, 'watch_glass', 'watch')]
    parts.append((G.head_proxy(cfg.get('hat')), 'shadow', 'shadow'))
    return parts, tc


class PovCharacter:
    def __init__(self, cam, profile='sarajevo_civilian_1914', ground=None, subdiv=2, tag='pov'):
        if profile not in O.PROFILES:
            raise ValueError(f'Perfil desconhecido: {profile}. Perfis: {", ".join(O.PROFILES)}')
        self.cam, self.profile, self.cfg, self.ground = cam, profile, O.PROFILES[profile], ground
        self.rest = S.solve(rest_params())
        self.root = bpy.data.objects.new(f'{tag}_root', None)
        link(self.root)
        mats = _materials(self.cfg, tag)
        parts, torso_cage = build_parts(self.cfg, self.rest)
        mats['torso'] = MT.fabric(f'{tag}_torso', self.cfg['colors'][self.cfg['torso']['fabric']],
                                  quilt=self.cfg['torso'].get('quilt'),
                                  seams=_front_seams(self.cfg['torso'], torso_cage.circ),
                                  rough=0.92 if self.cfg['torso']['fabric'] != 'jacket' else 0.86)
        mats['shadow'] = MT.flat(f'{tag}_shadow', (0.05, 0.05, 0.05), 0.9)
        self.parts = [self._make(cage, mats[key], group, subdiv) for cage, key, group in parts]
        for part in self.parts:
            if part['group'] == 'shadow':          # cabeça e chapéu: só projetam sombra
                ob = part['ob']
                ob.visible_camera = ob.visible_diffuse = ob.visible_glossy = False
                ob.visible_transmission = ob.visible_volume_scatter = False

    def _make(self, cage, material, group, subdiv):
        V, bones, Wm = cage.arrays()
        me = bpy.data.meshes.new(cage.name)
        me.from_pydata(V.tolist(), [], [tuple(f) for f in cage.F])
        uv = me.uv_layers.new(name='UVMap')
        uv.data.foreach_set('uv', np.array([c for f in cage.FUV for c in f], np.float32).ravel())
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
        rest_co = me.attributes.new('pov_rest', 'FLOAT_VECTOR', 'POINT')   # textura presa à pele
        rest_co.data.foreach_set('vector', V.astype(np.float32).ravel())
        me.materials.append(material)
        me.update()
        ob = bpy.data.objects.new(cage.name, me)
        link(ob)
        ob.parent = self.root
        ob.matrix_parent_inverse = Matrix.Identity(4)
        mod = ob.modifiers.new('subdiv', 'SUBSURF')
        mod.levels, mod.render_levels = 1, subdiv
        mod.uv_smooth = 'PRESERVE_BOUNDARIES'
        if getattr(cage, 'fuse', False):                    # mão: tubos fundidos numa superfície só
            mod.levels = mod.render_levels = 1
            add_fuse(ob, material)
        ob['pov_group'] = group or ''
        rest = [(self.rest[b][0], self.rest[b][1]) for b in bones]
        return {'ob': ob, 'me': me, 'V': V, 'bones': bones, 'W': Wm, 'rest': rest, 'group': group}

    def place(self, cam=None, heading=None):
        """Põe a origem do corpo sob a câmera, virada para o rumo da caminhada."""
        cam = cam or self.cam
        R = np.array(cam.rotation_euler.to_matrix())
        fwd = R @ np.array([0, 0, -1.0])
        root, yaw = M.body_from_camera(np.array(cam.location), fwd, heading)
        self.root.location = tuple(root)
        self.root.rotation_euler = (0.0, 0.0, yaw)
        self.head_pitch = math.asin(max(-1.0, min(1.0, float(fwd[2]))))
        return root

    def pose(self, t, speed=0.0, actions=(), step_hz=1.8, dz=0.0):
        p = M.pose_params(t, speed, step_hz, actions, self.cfg)
        p['props']['head'] = (S.RX(getattr(self, 'head_pitch', 0.0)), S.HEAD_PIVOT.copy())
        if dz:
            for side in ('R', 'L'):
                p['legs'][side]['A'] = p['legs'][side]['A'] - np.array([0, 0, dz])
        return p, S.solve(p)

    def update(self, t, cam=None, speed=0.0, actions=(), heading=None, step_hz=1.8):
        """Pose do tempo t. speed em m/s (0 parado), heading em rad (0 = +Y), actions como em motion.py."""
        root = self.place(cam, heading)
        dz = 0.0
        if self.ground is not None:                      # pés no chão apesar do balanço da câmera
            dz = max(-0.06, min(0.06, root[2] - self.ground))
        p, bones = self.pose(t, speed, actions, step_hz, dz)
        shown = p['shown']
        for part in self.parts:
            g = part['group']
            vis = g in (None, 'shadow') or shown.get(g, 0.0) >= (0.02 if g == 'rifle' else 0.35)
            part['ob'].hide_render = part['ob'].hide_viewport = not vis
            # peças ocultas também são recalculadas: o estado nunca depende do frame anterior
            V = part['V']
            out = np.zeros_like(V)
            for j, b in enumerate(part['bones']):
                R0, h0 = part['rest'][j]
                R, h = bones[b]
                out += part['W'][:, j:j + 1] * (((V - h0) @ R0) @ R.T + h)
            part['me'].vertices.foreach_set('co', out.ravel())
            part['me'].update()
        return None


def create_character(cam, profile='sarajevo_civilian_1914', **kw):
    return PovCharacter(cam, profile, **kw)
