from pyparticles.particles import types
from pyparticles.engine import sim as simulation
import pygame

if __name__ == '__main__':
    pygame.init()
    sim = simulation.ParticleSim((30, 30), (12, 12), bg_clr='pink')
    sim.add_particle(types.TestParticle(), (0, 0))
    sim.add_particle(types.TestParticle(), (7, 9))
    sim.add_particle(types.TestParticle(), (15, 5))
    sim.add_particle(types.TestParticle(), (28, 2))
    sim.add_particle(types.TestParticle(), (7, 3))

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        sim.update()
        screen.blit(sim.image, (0, 0))
        pygame.display.flip()
        clock.tick(2)
