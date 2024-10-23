from enum import Enum
from typing import TYPE_CHECKING
import pygame
from pyparticles.engine.utils import rand_iter, Point
from random import random

if TYPE_CHECKING:
    from pyparticles.engine.simulation import ParticleSim

# NOTE: this only works on Python 3.10 and LOWER
# For Python 3.11+, use StrEnume
class UpdateKwarg(str, Enum):
    FRAME: str = 'current_frame'
    SIM: str = 'simulation_world'
    FUNCS: str = 'particle_behaviors'

class ParticleUpdate(Exception):
    pass

class BaseParticle(pygame.sprite.Sprite):

    image: pygame.Surface
    rect: pygame.Rect
    frame: int
    active: bool
    keep_active: bool
    dependants: list['BaseParticle']
    depends_on: list[Point]

    def __init__(self, *args) -> None:
        groups = []
        for arg in args:
            if isinstance(arg, pygame.sprite.Group):
                groups.append(arg)
        pygame.sprite.Sprite.__init__(self, *groups)
        # initialize attributes to default values
        self.image = None # type: ignore
        self.rect = None # type: ignore
        self.frame = -1
        self.active = True
        self.keep_active = False # True if updated or could be updated
        self.dependants = []
        # Vector list of particles this depends on to be activated. Values are set by the init
        # functions of subclasses, and this list remains unchanged afterwards. If this particle
        # fails to update and all the particles it depends on are deactivated, then this particle
        # will deactivate.
        self.depends_on = []

    # def pos_as_point(self) -> Point:
    #     return Point(self.rect.topleft)

    def updateable(self, current_frame: int) -> bool:
        # TODO: do we want this to require that the particle be active?
        return self.active and self.frame < current_frame

    def add_dependant(self, particle: 'BaseParticle') -> None:
        self.dependants.append(particle)

    def activate(self) -> None:
        # sanity check
        if self.active:
            print('Already active!')
            return
        self.active = True
        self.activate_dependants()

    def activate_dependants(self) -> None:
        while len(self.dependants) > 0:
            self.dependants.pop().activate()

    def update(self, **kwargs) -> None:
        # pre update - make sure we haven't already updated and update attributes
        current_frame = kwargs[UpdateKwarg.FRAME]
        if current_frame <= self.frame:
            print('Already updated')
            return
        self.frame = current_frame
        self.keep_active = False
        # update - do specific behaviors until we update
        try:
            for behavior in kwargs[UpdateKwarg.FUNCS]:
                behavior(self, **kwargs)
        except ParticleUpdate:
            # TODO: we need a better way to reset certain particle attributes when this particle is updated
            self.heap.stuck = False
            self.keep_active = True
        # post-update - check if the particle is still active
        self.active = self.keep_active
        sim: ParticleSim = kwargs[UpdateKwarg.SIM]
        sim.remove_from_queue(self)
        if self.active:
            self.activate_dependants()
            return
        pos = sim.get_particle_pos(self)
        for d in self.depends_on:
            _, p = sim.get_cell(pos + d)
            if p is not None:
                p.add_dependant(self)

class GravitySpec():

    vec: Point
    prob: float

    def __init__(self, vec: Point = Point(0, 1), prob: float = 1.0) -> None:
        self.vec = vec
        self.prob = prob

    def copy(self):
        return GravitySpec(self.vec, self.prob)

class GravityParticle(BaseParticle):

    gravity: GravitySpec

    def __init__(self, *args):
        super().__init__(*args)
        self.gravity = GravitySpec()
        for arg in args:
            if isinstance(arg, GravitySpec):
                self.gravity = arg.copy()
                break
        self.depends_on.append(self.gravity.vec)

    def update(self, **kwargs):
        sim = kwargs[UpdateKwarg.SIM]
        frame = kwargs[UpdateKwarg.FRAME]
        # get our destination position
        dest_pos = sim.get_particle_pos(self) + self.gravity.vec
        for attempt in range(2):
            # check that the destination is in bounds and empty
            dest_valid, dest_cell = sim.get_cell(dest_pos)
            if not dest_valid:
                return
            if dest_cell is None:
                sim.move_particle(self, dest_pos)
                raise ParticleUpdate()
            if attempt == 0 and dest_cell.updateable(frame):
                dest_cell.update(**kwargs)
            # TODO: do we need this?
            # maybe not after adding a call to `update()` in the `activate()` function
            if attempt == 1 and dest_cell.active:
                self.keep_active = True

class HeapSpec():
    vecs: list[Point]
    prob: float
    lims: dict[tuple[int, int], Point]
    stuck: bool

    def __init__(self, vecs: list[Point] = [], prob: float = 1.0, lims: dict[tuple[int, int], Point] = {}) -> None:
        self.stuck = False
        self.lims = {}
        for k, v in lims.items():
            self.lims[k] = Point(v)
        self.prob = prob
        self.vecs = []
        if prob < 1.0:
            for v in vecs:
                self.vecs.append(Point(v))
        else:
            for v in vecs:
                self.lims[(v.x, v.y)] = Point(v)

    def copy(self):
        return HeapSpec(self.vecs, self.prob, self.lims)

class HeapParticle(BaseParticle):

    heap: HeapSpec

    def __init__(self, *args):
        super().__init__(*args)
        self.heap = HeapSpec()
        for arg in args:
            if isinstance(arg, HeapSpec):
                self.heap = arg.copy()
                break
        for v in self.heap.vecs:
            self.depends_on.append(v)
        for k, v in self.heap.lims.items():
            self.depends_on.append(v)

    def update(self, **kwargs):
        sim: ParticleSim = kwargs[UpdateKwarg.SIM]
        frame: int = kwargs[UpdateKwarg.FRAME]
        # get our current position
        self_pos = sim.get_particle_pos(self)
        # check limits
        for lim in rand_iter(list(self.heap.lims.keys())):
            lim_valid, lim_cell = sim.get_cell(self_pos + lim)
            if not lim_valid:
                continue
            for attempt in range(2):
                if lim_cell is None:
                    sim.move_particle(self, self_pos + self.heap.lims[lim])
                    raise ParticleUpdate()
                if attempt == 0 and lim_cell.updateable(frame):
                    lim_cell.update(**kwargs)
                if attempt == 1 and lim_cell.active:
                    self.keep_active = True
        # limits didn't trigger - check probabilistic vectors if not stuck
        if self.heap.stuck:
            return
        for vec in rand_iter(self.heap.vecs):
            dest_valid, dest_cell = sim.get_cell(self_pos + vec)
            if not dest_valid:
                continue
            for attempt in range(2):
                if dest_cell is None:
                    if random() < self.heap.prob:
                        sim.move_particle(self, self_pos + vec)
                        raise ParticleUpdate()
                    else:
                        self.heap.stuck = True
                        # TODO: make this the same as everything else
                        # Update exception or add a new exception to determine when we should reset states
                        return
                if attempt == 0 and dest_cell.updateable(frame):
                    dest_cell.update(**kwargs)
                if attempt == 1 and dest_cell.active:
                    self.keep_active = True