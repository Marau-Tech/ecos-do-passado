"""Sistema reutilizável de personagens em primeira pessoa (compatibilidade).

A implementação fica no pacote engine/pov/ (esqueleto, geometria, roupas, movimento). Este
arquivo mantém a API antiga:

    update = create_pov_character(cam, 'sarajevo_civilian_1914')
    update(t, walking=True)

Para controlar velocidade, rumo e ações (relógio, proteção, fuzil), use o objeto direto:

    from pov import create_character
"""
from pov.outfits import PROFILES
from pov.character import create_character

__all__ = ['PROFILES', 'create_pov_character', 'create_character']


def create_pov_character(cam, profile='sarajevo_civilian_1914', speed=0.7, **kw):
    """Cria o personagem preso à câmera e devolve update(t, walking=True, actions=(), heading=None)."""
    ch = create_character(cam, profile, **kw)

    def update(t, walking=True, actions=(), heading=None):
        return ch.update(t, cam, speed=speed if walking else 0.0, actions=actions, heading=heading)

    update.character = ch
    return update
