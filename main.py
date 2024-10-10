import pygame
from math import sqrt
from pyparticles.objects import particles
from pyparticles.engine import simulation
from pyparticles.engine.utils import Point
from random import randint
import cProfile, pstats, io
from pstats import SortKey

### FAR FUTURE PROJECTS ###
# TODO: Update code to use type hints
#       Attribute type hints will be placed between class docstring and __init__()
# TODO: Update docstrings once typehints have been added
### NEAR FUTURE PROJECTS ###
# TODO: Add module-level docstrings

brush_size = 1

def print_info(abs_pos, sim):
    pos = sim.abs_to_grid(Point(abs_pos))
    _, cell = sim.get_cell(pos)
    if cell is None:
        print('Empty cell! No info to print...')
        return
    print(f'Selected {cell}')
    pos = sim.get_particle_pos(cell)
    print(f'  Cell located at: {pos.x},{pos.y}')
    #print(f'  Cell dirty is: {cell.updated}')
    #print(f'  Cell can be updated: {cell._updateable}')
    print(f'  Cell state is: {cell.active}')
    #print(f'  Cell stuck is: {cell.heap.stuck}')
    #depends_on = []
    #for p in sim._particle_group:
    #    if cell in p._dependants:
    #        depends_on.append(p)
    print(f'Depends on {len(cell.depends_on)} other cells to remain inactive')
    #for d in depends_on:
    #    d_pos = sim.get_pos(d.rect.topleft)
    #    print(f'  Depends on cell at {d_pos.x},{d_pos.y} with active state: {d.active}')

def paint(sim, adding):
    pos = sim.abs_to_grid(Point(pygame.mouse.get_pos()))
    for x in range(-1*brush_size, brush_size+1, 1):
        for y in range(-1*brush_size, brush_size+1, 1):
            off = Point(x, y)
            if not sim.in_bounds(pos + off):
                continue
            if sqrt(x**2 + y**2) > brush_size:
                continue
            if adding:
                sim.add_particle(particles.TestParticle(), pos + off)
            else:
                sim.remove_particle(pos + off)

def main():
    pygame.init()
    sim = simulation.ParticleSim((40, 40), (12, 12), background='black')

    screen = pygame.display.set_mode((40*12, 40*12))
    clock = pygame.time.Clock()

    running = True
    tick = 0.0
    fps = 60
    tickrate = 0.4 # percent of frames to update sim on
    tickrate = 1 / tickrate
    adding = False
    removing = False

    #sim.add_particle(particles.TestParticle(), (10,46))
    #sim.add_particle(particles.TestParticle(), (10,47))

    global brush_size

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

def test_draw_perf(pr, dirty=False, moving=False):
    pygame.init()

    SPRITE_SIZE = 5
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 600
    MIN_RGB = 50
    MAX_RGB = 255
    MAX_LOOPS = 500

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    sprites = None
    bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    bg_surf.fill('black')

    if dirty:
        sprites = pygame.sprite.LayeredDirty()
    else:
        sprites = pygame.sprite.Group()
    for x in range(0, SCREEN_WIDTH, SPRITE_SIZE):
        for y in range(0, SCREEN_HEIGHT, SPRITE_SIZE):
            s = None
            if dirty:
                s = pygame.sprite.DirtySprite()
            else:
                s = pygame.sprite.Sprite()
            s.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE)).convert()
            s.image.fill(pygame.Color(randint(MIN_RGB, MAX_RGB), randint(MIN_RGB, MAX_RGB), randint(MIN_RGB, MAX_RGB)))
            s.rect = s.image.get_rect()
            s.rect.topleft = (x, y)
            sprites.add(s)

    pr.enable()
    loops = 0
    while loops < MAX_LOOPS:
        # poll to avoid the 'not responding' message
        pygame.event.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pr.disable()
                return
        # drawing
        if dirty:
            sprites.draw(screen, bg_surf)
        else:
            screen.fill('black')
            sprites.draw(screen)
        pygame.display.flip()
        # move sprites (if enabled)
        if moving:
            for s in sprites:
                x, y = s.rect.topleft
                x += SPRITE_SIZE
                if x >= SCREEN_WIDTH:
                    x = 0
                    y += SPRITE_SIZE
                    if y >= SCREEN_HEIGHT:
                        y = 0
                s.rect.topleft = (x, y)
                if dirty:
                    s.dirty = 1
        # tick the clock and print the FPS
        #clock.tick()
        #print(clock.get_fps())
        loops += 1
    pr.disable()

class RandSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.val = randint(0, 1)

    def update(self):
        self.val = randint(0, 1)

def test_loop_perf(pr, num=8000, max_loops=500, group=False):
    update_group = pygame.sprite.Group()
    sprites = None
    if group:
        sprites = pygame.sprite.Group()
    else:
        sprites = []
    for x in range(num):
        s = RandSprite()
        if group:
            sprites.add(s)
        else:
            sprites.append(s)
        update_group.add(s)
    loops = 0
    pr.enable()
    while loops < max_loops:
        l = [s for s in sprites if s.val == 1]
        #l = []
        #for s in sprites:
        #    if s.val == 1:
        #        l.append(s)
        update_group.update()
        loops += 1
    pr.disable()

class TestClass():
    def __init__(self):
        self.val = 0

    def do_a_thing(self):
        self.val = randint(0, 100)
        return (self.val % 2) == 1

def test_func_perf(pr, reassign=False, count=100000):
    if reassign:
        test_func_perf_other(pr, count)
        return
    c = TestClass()
    loops = 0
    pr.enable()
    while loops < count:
        c.do_a_thing()
        loops += 1
    pr.disable()

def test_func_perf_other(pr, count):
    c = TestClass()
    f = c.do_a_thing
    loops = 0
    pr.enable()
    while loops < count:
        f()
        loops += 1
    pr.disable()

if __name__ == '__main__':
    PROFILE_MAIN = False
    PROFILE_TEST = False

    if PROFILE_MAIN:
        pr = cProfile.Profile()
        main()
        st = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=st).sort_stats(sortby)
        ps.print_stats()
        print(st.getvalue())
    else:
        main()

    if not PROFILE_TEST:
        exit(0)

    func_type = ['Reassigned', 'Dotted']
    for i in range(2):
        pr = cProfile.Profile()
        test_func_perf(pr, reassign=(i==1))
        st = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=st).sort_stats(sortby)
        ps.print_stats()
        print(f'{func_type[i]}')
        print('--------------------------------------------------')
        print(st.getvalue())
    #exit(0)

    group_type = ['list', 'group']
    for i in range(2):
        pr = cProfile.Profile()
        test_loop_perf(pr, group=(i==1))
        st = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=st).sort_stats(sortby)
        ps.print_stats()
        print(f'{group_type[i]}')
        print('--------------------------------------------------')
        print(st.getvalue())
    #exit(0)

    sprite_type = ['Normal', 'Dirty']
    movement_type = ['Stationary', 'Moving']
    for i in range(4):
        pr = cProfile.Profile()
        test_draw_perf(pr, dirty=((i%2)==1), moving=((i//2)==1))
        st = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=st).sort_stats(sortby)
        ps.print_stats()
        print(f'{sprite_type[i%2]}, {movement_type[i//2]}')
        print('--------------------------------------------------')
        print(st.getvalue())
