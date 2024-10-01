import pygame
from pyparticles.objects import properties

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
        self.image = pygame.Surface((10, 10))
        self.image.fill('brown')
        self.rect = self.image.get_rect()

    def update(self, **kwargs):
        self.pre_update()
        properties.GravityParticle.update(self, **kwargs)
        properties.HeapableParticle.update(self, **kwargs)
        properties.BaseParticle.update(self, **kwargs)