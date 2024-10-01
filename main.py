import pygame
from math import sqrt
from pyparticles.objects import particles
from pyparticles.engine import simulation
from pyparticles.engine.utils import Point

### FAR FUTURE PROJECTS ###
# TODO: Update code to use type hints
#       Attribute type hints will be placed between class docstring and __init__()
# TODO: Update docstrings once typehints have been added
### NEAR FUTURE PROJECTS ###
# TODO: Add module-level docstrings

brush_size = 1

def print_info(abs_pos, sim):
    pos = sim.get_pos(abs_pos)
    cell = sim.get_cell(pos)
    if cell is None:
        print('Empty cell! No info to print...')
        return
    print(f'Selected {cell}')
    pos = sim.get_pos(cell.rect.topleft)
    print(f'  Cell located at: {pos.x},{pos.y}')
    print(f'  Cell dirty is: {cell.dirty}')
    print(f'  Cell state is: {cell.active}')
    print(f'  Cell stuck is: {cell.heap.stuck}')
    depends_on = []
    for p in sim._particle_group:
        if cell in p._dependants:
            depends_on.append(p)
    print(f'Depends on {len(depends_on)} other cells to remain inactive')
    for d in depends_on:
        d_pos = sim.get_pos(d.rect.topleft)
        print(f'  Depends on cell at {d_pos.x},{d_pos.y} with active state: {d.active}')

def paint(sim, adding):
    pos = sim.get_pos(pygame.mouse.get_pos())
    for x in range(-1*brush_size, brush_size+1, 1):
        for y in range(-1*brush_size, brush_size+1, 1):
            off = Point(x, y)
            if not sim.in_bounds(pos + off):
                f = pos + off
                print(f'{f.x},{f.y} not in boundss')
                continue
            if sqrt(x**2 + y**2) > brush_size:
                continue
            if adding:
                sim.add_particle(particles.TestParticle(), pos + off)
            else:
                sim.remove_particle(pos + off)

if __name__ == '__main__':
    pygame.init()
    sim = simulation.ParticleSim((50, 50), (12, 12), bg_clr='pink')

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    running = True
    tick = 0.0
    fps = 60
    tickrate = 0.4 # percent of frames to update sim on
    tickrate = 1 / tickrate
    adding = False
    removing = False

    sim.add_particle(particles.TestParticle(), (10,46))
    sim.add_particle(particles.TestParticle(), (10,47))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    adding = True
                elif event.button == 3:
                    removing = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    adding = False
                elif event.button == 3:
                    removing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    print_info(pygame.mouse.get_pos(), sim)
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    brush_size += 1
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    brush_size -= 1
                    if brush_size < 0:
                        brush_size = 0
        if adding:
            paint(sim, True)
        if removing:
            paint(sim, False)
        tick += 1
        while tick >= tickrate:
            tick -= tickrate
            sim.update()
            print(clock.get_fps() // 1)
        screen.blit(sim.image, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
