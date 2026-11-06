from lib import *


def cube_vt(sx, sy, sz):
    """Vértices e triângulos de uma caixa com a base em z = 0, para o scatter."""
    x, y = sx / 2, sy / 2
    v = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0), (-x, -y, sz), (x, -y, sz), (x, y, sz), (-x, y, sz)]
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return v, f


def text3d(body, loc, size, color, strength, rot=(math.pi / 2, 0, 0), align='LEFT', font='DejaVuSansMono-Bold'):
    """Texto que brilha, virado para -Y."""
    c = bpy.data.curves.new('txt', 'FONT')
    c.font = bpy.data.fonts.load(f'/usr/share/fonts/truetype/dejavu/{font}.ttf')
    c.body = body; c.size = size; c.align_x = align; c.space_line = 1.15
    c.materials.append(emission('txt' + body[:4], color, strength))
    o = bpy.data.objects.new('txt', c); link(o)
    o.location = loc; o.rotation_euler = rot
    return o


def planet_terminal(r=1.0, loc=(0, 0, 0)):
    """telhados de vidro cinza em grade, pistas e luzes laranja"""
    m, nt = mat('terminal')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    b = n(nt, 'ShaderNodeTexBrick', Scale=14.0, Mortar_Size=0.03); L(nt, tc, b.inputs['Vector'])
    b.inputs['Color1'].default_value = (0.42, 0.44, 0.46, 1); b.inputs['Color2'].default_value = (0.55, 0.56, 0.58, 1)
    b.inputs['Mortar'].default_value = (0.12, 0.12, 0.13, 1)
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=60.0); L(nt, tc, v.inputs['Vector'])
    lights = mix(nt, math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.08), (0, 0, 0), (1.0, 0.55, 0.2))
    out(nt, principled(nt, b.outputs['Color'], 0.35, spec=0.6, emis=lights, emis_str=3.0).outputs[0])
    return sphere('p_terminal', r, loc, m, 192, 96)


def planet_neon(r=1.0, loc=(0, 0, 0)):
    """noite inteira coberta por uma malha de neon magenta e ciano"""
    m, nt = mat('neon')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    b = n(nt, 'ShaderNodeTexBrick', Scale=45.0, Mortar_Size=0.012); L(nt, tc, b.inputs['Vector'])
    b.inputs['Color1'].default_value = (0, 0, 0, 1); b.inputs['Color2'].default_value = (0, 0, 0, 1)
    b.inputs['Mortar'].default_value = (1, 1, 1, 1)
    a = n(nt, 'ShaderNodeTexNoise', Scale=3.0, Detail=4.0); L(nt, tc, a.inputs['Vector'])
    hue = mix(nt, math_(nt, 'GREATER_THAN', a.outputs['Fac'], 0.5), (1.0, 0.1, 0.7), (0.1, 0.9, 1.0))
    city = n(nt, 'ShaderNodeTexNoise', Scale=2.2, Detail=6.0); L(nt, tc, city.inputs['Vector'])
    mask = ramp(nt, [(0.45, (0, 0, 0)), (0.6, (1, 1, 1))], city.outputs['Fac']).outputs[0]   # cidade em manchas, o resto escuro
    emis = mix(nt, 1.0, mix(nt, 1.0, b.outputs['Color'], hue, 'MULTIPLY'), mask, 'MULTIPLY')
    out(nt, principled(nt, (0.02, 0.02, 0.03), 0.4, emis=emis, emis_str=2.5).outputs[0])
    return sphere('p_neon', r, loc, m, 192, 96)


def planet_noon(r=1.0, loc=(0, 0, 0)):
    """branco liso, sem nada"""
    m, nt = mat('noon')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    a = n(nt, 'ShaderNodeTexNoise', Scale=1.5, Detail=2.0); L(nt, tc, a.inputs['Vector'])
    col = ramp(nt, [(0.4, (0.88, 0.87, 0.84)), (0.6, (0.97, 0.96, 0.93))], a.outputs['Fac']).outputs[0]
    out(nt, principled(nt, col, 0.6, spec=0.2).outputs[0])
    return sphere('p_noon', r, loc, m, 192, 96)


def planet_market(r=1.0, loc=(0, 0, 0)):
    """telhado bege sem fim, com fileiras de claraboias acesas"""
    m, nt = mat('market')
    tc = n(nt, 'ShaderNodeTexCoord').outputs['Object']
    b = n(nt, 'ShaderNodeTexBrick', Scale=30.0, Mortar_Size=0.0, Brick_Width=0.5, Row_Height=0.12); L(nt, tc, b.inputs['Vector'])
    b.inputs['Color1'].default_value = (0.72, 0.66, 0.52, 1); b.inputs['Color2'].default_value = (0.66, 0.60, 0.48, 1)
    v = n(nt, 'ShaderNodeTexVoronoi', Scale=50.0); L(nt, tc, v.inputs['Vector'])
    sky = mix(nt, math_(nt, 'LESS_THAN', v.outputs['Distance'], 0.1), (0, 0, 0), (0.85, 0.95, 1.0))
    out(nt, principled(nt, b.outputs['Color'], 0.7, spec=0.2, emis=sky, emis_str=1.5).outputs[0])
    return sphere('p_market', r, loc, m, 192, 96)


def glow(r, loc, color, strength):
    """halo: forte no centro, some na borda"""
    m, nt = mat('glow')
    lw = n(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    a = math_(nt, 'POWER', math_(nt, 'SUBTRACT', 1.0, lw.outputs['Facing']), 3.0)
    e = n(nt, 'ShaderNodeEmission', Strength=strength); e.inputs['Color'].default_value = (*color, 1)
    tr = n(nt, 'ShaderNodeBsdfTransparent')
    ms = n(nt, 'ShaderNodeMixShader')
    L(nt, a, ms.inputs[0]); L(nt, tr.outputs[0], ms.inputs[1]); L(nt, e.outputs[0], ms.inputs[2])
    out(nt, ms.outputs[0])
    return sphere('glow', r, loc, m, 48, 24)


def orbit(planet, atmo_color, sd, tilt=(0.3, -0.2, 0), extra=None):
    """take de abertura: planeta girando com a câmera parada enquanto o nome é dito, depois zoom"""
    from timeline import NAME_HOLD
    reset(20)
    world_space((0.02, 0.014, 0.022), 1.0)
    sun(4.5, sd, (1, 0.96, 0.92))
    p = planet(1.0); atmosphere(1.0, atmo_color, sd, 1.03, power=5, strength=0.55)
    p.rotation_euler = tilt
    if extra: extra()
    cam = camera((0, -3.6, 0), (0, 0, 0), 40)
    def update(t, u, dur):
        u = zoom_after(t, NAME_HOLD, dur)
        p.rotation_euler.z = 0.8 + 0.1 * t
        cam.location = vlerp((0.1, -3.6, 0.1), (0.05, -2.3, 0.05), ease(u))
        look(cam, (-0.05 * u, 0, 0))
    return update
