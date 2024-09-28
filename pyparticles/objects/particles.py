import pygame
from pyparticles.objects import properties

class TestParticle(
    #properties.HeapableParticle,
    properties.GravityParticle,
    properties.BaseParticle):
    """Test particle

    TODO: replace with actual particle later
    """

    def __init__(self, **kwargs):
        norm = [(1,1),(-1,1)]
        test = [(1,0),(-1,0)]
        super().__init__(**kwargs, gravity_v=(0,1), heap_v=norm, heap_p=0.9)
        self.image = pygame.Surface((10, 10))
        self.image.fill('brown')
        self.rect = self.image.get_rect()

    def update(self, **kwargs):
        if self.dirty == 0:
            super().update(**kwargs)