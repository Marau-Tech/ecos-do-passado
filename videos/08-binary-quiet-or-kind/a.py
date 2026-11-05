"""A: o planeta quieto. Poeira cinza, pegadas que aparecem embaixo de você e o visor embaçando por fora."""
from lib import *
from planets import *
import timeline as TL

SHOTS = {'a1': 4.5, 'a2': 4.0, 'a3': 4.5}


def dust_mat():
    m, nt = mat('dust')
    pos = n(nt, 'ShaderNodeNewGeometry').outputs['Position']
    a = n(nt, 'ShaderNodeTexNoise', Scale=0.8, Detail=8.0, Roughness=0.6); L(nt, pos, a.inputs['Vector'])
    col = ramp(nt, [(0.35, (0.42, 0.42, 0.43)), (0.65, (0.6, 0.6, 0.61))], a.outputs['Fac']).outputs[0]
    f = n(nt, 'ShaderNodeTexNoise', Scale=9.0, Detail=6.0, Roughness=0.6); L(nt, pos, f.inputs['Vector'])
    bp = n(nt, 'ShaderNodeBump', Strength=0.4, Distance=0.03); L(nt, f.outputs['Fac'], bp.inputs['Height'])
    out(nt, principled(nt, col, 0.98, spec=0.05, normal=bp.outputs[0]).outputs[0])
    return m


def plain():
    reset(20)
    world_flat((0.5, 0.5, 0.52), 0.8)
    box('ground', (400, 400, 0.1), (0, 0, -0.05), dust_mat())
    sun(2.0, (-0.4, -0.3, 0.6), (1, 1, 1), 8.0)
    fog((0.5, 0.5, 0.52), 2.0, 26.0)


def build_a1():
    reset(20)
    world_space((0.015, 0.012, 0.02), 1.0)
    sd = (-1.0, -0.3, 0.3)
    sun(4.2, sd, (1, 0.98, 0.96))
    p = planet_quiet(1.0); atmosphere(1.0, (0.8, 0.8, 0.82), sd, 1.015, power=6, strength=0.3)
    p.rotation_euler = (0.25, -0.15, 0)
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u):
        u = zoom_after(t, TL.NAME_HOLD, SHOTS['a1'])
        p.rotation_euler.z = 0.6 + 0.1 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update


def build_a2():
    """Primeira pessoa olhando para baixo: as pegadas aparecem logo depois de você passar."""
    plain()
    pm = simple('print', (0.22, 0.22, 0.23), 0.98)
    prints = []
    for k in range(14):
        o = sphere('print', 0.13, (0.16 if k % 2 else -0.16, 0.75 * k - 1.0, -0.035), pm, 16, 8)
        o.scale = (0.75, 1.7, 0.4)
        prints.append(o)
    cam = camera((0, 0, 1.6), (0, 2.4, 0), 30)
    def update(t, u):
        y = 1.15 * t
        bob = 0.025 * abs(math.sin(math.pi * 1.55 * t))
        cam.location = (0.02 * math.sin(math.pi * 1.55 * t), y - 0.3, 1.6 + bob)
        look(cam, (0, y + 2.2, 0))
        for o in prints:
            o.hide_render = o.location.y > y + 1.1        # nasce na borda de baixo do quadro, no seu passo
    return update


def build_a3():
    """O visor embaça em manchas que crescem no ritmo de uma respiração, do lado de fora."""
    plain()
    cam = camera((0, 0, 1.6), (0, 12, 1.1), 30)
    m, nt = mat('visor')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    off = n(nt, 'ShaderNodeVectorMath', {'operation': 'SUBTRACT'}); L(nt, tc, off.inputs[0]); off.inputs[1].default_value = (0.02, 0.0, 0.01)
    tc = off.outputs[0]                                 # a mancha fica à direita do centro
    nz = n(nt, 'ShaderNodeTexNoise', Scale=14.0, Detail=6.0, Roughness=0.6); L(nt, tc, nz.inputs['Vector'])
    d = n(nt, 'ShaderNodeVectorMath', {'operation': 'LENGTH'}); L(nt, tc, d.inputs[0])
    val = n(nt, 'ShaderNodeValue'); val.outputs[0].default_value = 0.0
    radial = math_(nt, 'SUBTRACT', math_(nt, 'MULTIPLY', val.outputs[0], 1.0), d.outputs['Value'])
    k = math_(nt, 'ADD', radial, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', nz.outputs['Fac'], 0.5), 0.03))
    fac = ramp(nt, [(0.0, (0, 0, 0)), (0.02, (0.55, 0.55, 0.55))], k).outputs[0]
    grain = n(nt, 'ShaderNodeTexNoise', Scale=60.0, Detail=4.0, Roughness=0.7); L(nt, tc, grain.inputs['Vector'])
    fac = math_(nt, 'MULTIPLY', fac, math_(nt, 'ADD', math_(nt, 'MULTIPLY', grain.outputs['Fac'], 0.8), 0.6))   # vapor manchado
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    fogc = n(nt, 'ShaderNodeEmission', Strength=0.9); fogc.inputs['Color'].default_value = (0.88, 0.9, 0.92, 1)
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, fac, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, fogc.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    visor = mesh_from('visor', [(-0.2, 0, -0.15), (0.2, 0, -0.15), (0.2, 0, 0.15), (-0.2, 0, 0.15)], [(0, 1, 2, 3)], m)
    visor.parent = cam
    visor.location = (0.0, 0.0, -0.12)               # na frente da lente
    visor.rotation_euler = (math.pi / 2, 0, 0)
    stem = bpy.data.objects.new('breath_at', None); link(stem)
    def update(t, u):
        s = max(0.0, t - TL.FOG_FROM)
        breath = 0.5 - 0.5 * math.cos(2 * math.pi * TL.BREATH * s)
        val.outputs[0].default_value = min(0.055, 0.006 * s + 0.025 * breath * min(1.0, s))
        return None
    return update
