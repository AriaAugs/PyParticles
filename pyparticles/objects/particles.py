import pygame
from random import randint
from pyparticles.objects import properties

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
    properties.HeapableParticle,
    properties.GravityParticle,
    properties.BaseParticle):
    """Test particle

    TODO: replace with actual particle later
    """

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            gravity_vec = (0, 1),
            heap_vec = [(1,1), (-1,1)],
            heap_prob = 0.5,
            heap_limit = [(1,2),(-1,2)]
        )
        self.image = _SPRITES[randint(0, 1)][randint(0, 1)]
        self.rect = _sprite_rect.copy()

    def update(self, **kwargs):
        self.pre_update()
        properties.GravityParticle.update(self, **kwargs)
        properties.HeapableParticle.update(self, **kwargs)
        properties.BaseParticle.update(self, **kwargs)