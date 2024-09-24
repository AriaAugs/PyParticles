import pygame
from pyparticles.particles import properties

class TestParticle(
    properties.GravityParticle,
    properties.BaseParticle):
    """Test particle

    TODO: replace with actual particle later
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = pygame.Surface(0, 0, 10, 10)
        self.image.fill('brown')
        self.rect = self.image.get_rect()
