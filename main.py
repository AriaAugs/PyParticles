import pygame
from pyparticles.objects import particles
from pyparticles.engine import simulation

### FAR FUTURE PROJECTS ###
# TODO: Update code to use type hints
#       Attribute type hints will be placed between class docstring and __init__()
# TODO: Update docstrings once typehints have been added
### NEAR FUTURE PROJECTS ###
# TODO: Add module-level docstrings

if __name__ == '__main__':
    pygame.init()
    sim = simulation.ParticleSim((50, 50), (12, 12), bg_clr='pink')

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    print(particles.TestParticle.__mro__)

    running = True
    tick = 0.0
    fps = 60
    tickrate = 0.4 # percent of frames to update sim on
    tickrate = 1 / tickrate
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
            sim.add_particle(particles.TestParticle(), pos)
        tick += 1
        while tick >= tickrate:
            tick -= tickrate
            sim.update()
        screen.blit(sim.image, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
