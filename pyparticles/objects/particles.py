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
        norm = [(1,1),(-1,1)]
        #test = [(1,0),(-1,0)]
        super().__init__(**kwargs, gravity_vec=(0, 1), heap_vec=[(1,1), (-1,1)], heap_prob=1.0, heap_limit=[(1,2),(-1,2)])
        self.image = pygame.Surface((10, 10))
        self.image.fill('brown')
        self.rect = self.image.get_rect()

    def update(self, **kwargs):
        self.updateable = False
        self.updateable |= properties.GravityParticle.update(self, **kwargs)
        self.updateable |= properties.HeapableParticle.update(self, **kwargs)
        if self.dirty != 0 and not self.updateable:
            print('Dirty bit set but is_updateable is False!')
            self.updateable = True