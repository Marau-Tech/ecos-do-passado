"""Os dois planetas, as pedras soltas, o chão e as peças do traje, usados pela intro e pelos dois trechos."""
from lib import *
import timeline as TL


def planet_heavy(r=1.0, loc=(0, 0, 0)):
    """ferro e ferrugem, achatado nos polos pela gravidade"""
    m, nt = mat('heavy')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.0, Detail=9.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.32, (0.16, 0.06, 0.03)), (0.5, (0.42, 0.16, 0.07)), (0.68, (0.55, 0.3, 0.16))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=26.0, Detail=6.0, Roughness=0.6); L(nt, tc, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.3, Distance=0.02); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.85, spec=0.2, normal=bp.outputs[0]).outputs[0])
    p = sphere('p_heavy', r, loc, m, 192, 96)
    p.scale = (1.0, 1.0, TL.FLAT)
    return p


def heavy_clouds(r=1.0, loc=(0, 0, 0)):
    """faixas de nuvem baixas e esticadas no sentido do equador"""
    m, nt = mat('hclouds')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    mp = n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 6.0); L(nt, tc, mp.inputs['Vector'])
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.5, Detail=6.0, Roughness=0.5); L(nt, mp.outputs[0], a.inputs['Vector'])
    fac = ramp(nt, [(0.5, (0, 0, 0)), (0.68, (1, 1, 1))], a.outputs['Fac']).outputs[0]
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    d = n(nt, 'ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value = (0.6, 0.42, 0.3, 1)
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, fac, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, d.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    c = sphere('hclouds', r * 1.008, loc, m, 128, 64)
    c.scale = (1.0, 1.0, TL.FLAT)
    return c


def planet_light(r=1.0, loc=(0, 0, 0)):
    """pedra-pomes clara, cinza e lilás, cheia de crateras rasas"""
    m, nt = mat('light')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=2.6, Detail=9.0, Roughness=0.55); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.42, 0.4, 0.46)), (0.66, (0.78, 0.76, 0.8))], a.outputs['Fac']).outputs[0]
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=9.0); L(nt, tc, v.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.5, Distance=0.04); L(nt, v.outputs['Distance'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return sphere('p_light', r, loc, m, 160, 80)


def rock_mat(name='rock', c=(0.5, 0.48, 0.52)):
    m, nt = mat(name)
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=6.0, Detail=6.0, Roughness=0.6); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.35, tuple(x * 0.55 for x in c)), (0.65, c)], a.outputs['Fac']).outputs[0]
    bp = n(nt, 'ShaderNodeBump', Strength=0.6, Distance=0.05); L(nt, a.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.1, normal=bp.outputs[0]).outputs[0])
    return m


def orbit_rocks(k, r0, r1, loc=(0, 0, 0), size=(0.03, 0.08), seed=4):
    """pedras soltas num anel inclinado em volta do planeta leve; devolve (pedra, raio, fase, altura)"""
    rs = np.random.RandomState(seed)
    m = rock_mat('orock')
    out_ = []
    for i in range(k):
        s = rs.uniform(*size)
        o = ico('orock', s, (0, 0, 0), m, 1)
        o.scale = (rs.uniform(0.7, 1.3), rs.uniform(0.7, 1.3), rs.uniform(0.6, 1.0))
        o.rotation_euler = tuple(rs.uniform(0, 6.28, 3))
        out_.append((o, rs.uniform(r0, r1), rs.uniform(0, 2 * math.pi), rs.uniform(-0.12, 0.12), Vector(loc)))
    return out_


def move_rocks(rocks, t, tilt=0.35):
    for o, r, ph, h, c in rocks:
        a = ph + 2 * math.pi * t / TL.ORBIT * (1.6 / r) ** 1.5
        x, y = r * math.cos(a), r * math.sin(a)
        z = h * r
        o.location = c + Vector((x, y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)))
        o.rotation_euler.z = a * 2


def ground(colors, name='dust', bump=0.4, scale=0.6):
    m, nt = mat(name)
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=scale, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, colors[0]), (0.65, colors[1])], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=9.0, Detail=6.0, Roughness=0.6); L(nt, pos, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=bump, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.95, spec=0.05, normal=bp.outputs[0]).outputs[0])
    return m


def pebbles(name, k, area, size, m, seed=2, z=0.0, flat=0.5):
    """cascalho espalhado: uma malha só"""
    rs = np.random.RandomState(seed)
    v, t = lathe([(0.0, -0.5), (0.8, -0.35), (1.0, 0.0), (0.75, 0.4), (0.0, 0.55)], 6)
    pos = np.stack([rs.uniform(area[0], area[1], k), rs.uniform(area[2], area[3], k), np.full(k, z)], 1)
    s = rs.uniform(size[0], size[1], k)
    sc = np.stack([s * rs.uniform(0.7, 1.3, k), s * rs.uniform(0.7, 1.3, k), s * flat], 1)
    return scatter(name, v, t, pos, rs.uniform(0, 6.28, k), sc, m)


def suit_mat():
    return simple('suit', (0.78, 0.77, 0.74), 0.7)


def glove(loc, yaw=0.0, s=1.0):
    """luva do traje espalmada no chão, dedos abertos para a frente (+Y); o braço sai para trás (-Y)"""
    root = bpy.data.objects.new('glove', None); link(root)
    root.location = loc; root.rotation_euler.z = yaw; root.scale = (s, s, s)
    sm = simple('glovem', (0.55, 0.55, 0.53), 0.75)
    grip = simple('grip', (0.08, 0.08, 0.09), 0.6)
    dark = simple('cuff', (0.12, 0.12, 0.13), 0.5, 0.4)
    arm = suit_mat()
    parts = []
    palm = ico('palm', 0.06, (0, 0, 0.028), sm, 3); palm.scale = (1.0, 1.05, 0.45); parts.append(palm)
    k = ico('knuckle', 0.06, (0, 0.035, 0.04), grip, 3); k.scale = (0.95, 0.3, 0.3); parts.append(k)
    for i, (dx, ang) in enumerate(((-0.042, -0.25), (-0.014, -0.08), (0.014, 0.08), (0.04, 0.22))):
        ln = (0.075, 0.09, 0.088, 0.07)[i]
        x0, y0 = dx, 0.05
        x1, y1 = x0 + math.sin(ang) * ln * 0.5, y0 + math.cos(ang) * ln * 0.5
        x2, y2 = x0 + math.sin(ang) * ln, y0 + math.cos(ang) * ln
        parts.append(tube('finger', [(x0, y0, 0.022), (x1, y1, 0.016), (x2, y2, 0.011)], [0.014, 0.013, 0.011], sm))
        parts.append(ico('tip', 0.011, (x2, y2, 0.011), grip, 2))
    parts.append(tube('thumb', [(-0.055, 0.0, 0.022), (-0.09, 0.03, 0.017), (-0.11, 0.065, 0.012)], [0.015, 0.014, 0.012], sm))
    parts.append(tube('cuff', [(0, -0.05, 0.035), (0, -0.09, 0.045)], [0.05, 0.056], dark, kind='POLY'))
    parts.append(tube('arm', [(0, -0.09, 0.045), (0.0, -0.35, 0.07), (0.0, -0.7, 0.1)], [0.05, 0.056, 0.06], arm))
    for o in parts:
        o.parent = root
    return root
