import pygame
from random import randint
from pyparticles.objects import properties
from pyparticles.engine.utils import Point

_SPRITE_SHEET = pygame.Surface((20, 20))
_sprite_rect = pygame.Rect(0, 0, 10, 10)
_SPRITE_SHEET.fill('sienna', _sprite_rect)
_sprite_rect.topleft = (0, 10)
_SPRITE_SHEET.fill('sienna1', _sprite_rect)
_sprite_rect.topleft = (10, 0)
_SPRITE_SHEET.fill('sienna2', _sprite_rect)
_sprite_rect.topleft = (10, 10)
_SPRITE_SHEET.fill('sienna3', _sprite_rect)
_SPRITES = [[
    _SPRITE_SHEET.subsurface(pygame.Rect(x*10, y*10, 10, 10))
    for x in range(2)] for y in range(2)]

class TestParticle(
    #properties.HeapableParticle,
    properties.GravityParticle,
    properties.BaseParticle):
    """Test particle

    TODO: replace with actual particle later
    """

    def __init__(self, **kwargs):
        super().__init__(
            properties.GravitySpec(vec = Point(0, 1), prob = 1.0)
            )
        self.image = _SPRITES[randint(0, 1)][randint(0, 1)]
        self.rect = _sprite_rect.copy()

    def update(self, **kwargs):
        kwargs[properties.UpdateKwarg.FUNCS] = [
            properties.GravityParticle.update
        ]
        properties.BaseParticle.update(self, **kwargs)
