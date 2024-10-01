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
        self.image = _SPRITE_SHEET
        self.rect = _sprite_rect.copy()
        self.source_rect = _sprite_rect.copy()
        indices = [0, 10]
        self.source_rect.top = indices[randint(0, 1)]
        self.source_rect.left = indices[randint(0, 1)]

    def update(self, **kwargs):
        self.pre_update()
        properties.GravityParticle.update(self, **kwargs)
        properties.HeapableParticle.update(self, **kwargs)
        properties.BaseParticle.update(self, **kwargs)