import pygame
from pyparticles.objects.properties import UpdateKwarg, BaseParticle
from typing import Optional
from pyparticles.engine.utils import Point
from random import randint

class ParticleSim():

    image: pygame.Surface
    _grid_size: Point
    _sim_grid: list[list[Optional[BaseParticle]]]
    _sim_frame: int
    _cell_size: Point
    _particles: pygame.sprite.Group
    _active_particles: list[BaseParticle]
    _update_queue: list[BaseParticle]
    _background: pygame.Surface

    def __init__(self, sim_size, cell_size, background) -> None:
        # sim size and sim representation
        self._grid_size = Point(sim_size)
        self._sim_grid = [
            [None for x in range(int(self._grid_size.x))]
            for y in range(int(self._grid_size.y))
        ]
        self._sim_frame = 0
        # cell size and sim image
        self._cell_size = Point(cell_size)
        image_size = (
            self._grid_size.x * self._cell_size.x,
            self._grid_size.y * self._cell_size.y
        )
        self.image = pygame.Surface(image_size)
        # groups for particles
        self._particles = pygame.sprite.Group()
        self._active_particles = []
        self._update_queue = []
        # TODO: need new particles list???
        if isinstance(background, pygame.Surface):
            self._background = background.copy()
        else:
            self._background = pygame.Surface(image_size)
            self._background.fill(background)

    def in_bounds(self, pos: Point) -> bool:
        return Point(0, 0) <= pos < self._grid_size

    def get_cell(self, pos: Point) -> tuple[bool, Optional[BaseParticle]]:
        if not self.in_bounds(pos):
            return (False, None)
        return (True, self._sim_grid[pos.y][pos.x])

    def grid_to_abs(self, grid_pos: Point) -> Point:
        return Point(grid_pos.x * self._cell_size.x, grid_pos.y * self._cell_size.y)

    def abs_to_grid(self, abs_pos: Point) -> Point:
        return Point(abs_pos.x // self._cell_size.x, abs_pos.y // self._cell_size.y)

    def get_particle_pos(self, particle: BaseParticle) -> Point:
        return self.abs_to_grid(Point(particle.rect.topleft))

    def clamp_pos(self, pos: Point) -> Point:
        return pos.clamp((0, 0), self._grid_size)

    def update(self, **kwargs):
        # update frame counter and active particle list
        self._sim_frame += 1
        # TODO: is it faster to create a new list every time?
        # TODO: is it faster to just iterate over all particles?
        for p in self._particles:
            if p.active and p not in self._active_particles:
                self._active_particles.append(p)
            if not p.active and p in self._active_particles:
                self._active_particles.remove(p)
        # update kwargs then update the particles in a random order
        kwargs[UpdateKwarg.SIM] = self
        kwargs[UpdateKwarg.FRAME] = self._sim_frame
        # TODO: would it help to remove particles from update list when recursive updates occur?
        # for p in rand_iter(self._active_particles):
        #     p.update(**kwargs)
        self._update_queue = self._active_particles[:]
        while self._update_queue:
            i = randint(0, len(self._update_queue) - 1)
            self._update_queue[i].update(**kwargs)
        # draw the image
        # TODO: do we need to blit the background first or can that be included in `draw()`?
        self.image.blit(self._background, (0, 0))
        self._particles.draw(self.image) # bgsurf = self._background)

    def remove_from_queue(self, particle: BaseParticle) -> None:
        self._update_queue.remove(particle)

    def move_particle(self, particle: BaseParticle, new_pos: Point) -> None:
        old_pos = self.get_particle_pos(particle)
        self._sim_grid[old_pos.y][old_pos.x] = None
        self._sim_grid[new_pos.y][new_pos.x] = particle
        particle.rect.topleft = tuple(self.grid_to_abs(new_pos))

    def add_particle(self, particle: BaseParticle, grid_pos: tuple[int, int]) -> bool:
        pos = Point(grid_pos)
        in_bounds, dest_cell = self.get_cell(pos)
        if not in_bounds or dest_cell is not None:
            return False
        self._sim_grid[pos.y][pos.x] = particle
        self._particles.add(particle)
        particle.rect.topleft = tuple(self.grid_to_abs(pos))
        return True

    def remove_particle(self, pos: Point) -> None:
        # get the particle to remove
        _, cell = self.get_cell(pos)
        if cell is None:
            return
        # active the particle's dependants
        cell.activate_dependants()
        # remove the particle from all sprite groups, the active particle list, and the sim grid
        cell.kill()
        if cell in self._active_particles:
            self._active_particles.remove(cell)
        self._sim_grid[pos.y][pos.x] = None
