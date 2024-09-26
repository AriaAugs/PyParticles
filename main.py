from pyparticles.particles import types
from pyparticles.engine import sim as simulation
import pygame

if __name__ == '__main__':
    pygame.init()
    sim = simulation.ParticleSim((50, 50), (12, 12), bg_clr='pink')
    sim.add_particle(types.TestParticle(), (0, 0))
    sim.add_particle(types.TestParticle(), (7, 9))
    sim.add_particle(types.TestParticle(), (15, 5))
    sim.add_particle(types.TestParticle(), (28, 2))
    sim.add_particle(types.TestParticle(), (7, 3))

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    running = True
    tick = 0
    fps = 60
    tickrate = 0.33 # percent of frames to update sim on
    tickrate = int(1 / tickrate)
    adding = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                adding = True
            if event.type == pygame.MOUSEBUTTONUP:
                adding = False
        if adding:
            pos = sim.get_pos(pygame.mouse.get_pos())
            sim.add_particle(types.TestParticle(), pos)
        tick = (tick + 1) % tickrate
        if tick == 0:
            sim.update()
        screen.blit(sim.image, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
