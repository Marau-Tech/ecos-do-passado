"""Personagem em primeira pessoa reutilizável (ver pov/README.md)."""


def create_character(*args, **kwargs):
    from .character import create_character as _create
    return _create(*args, **kwargs)
