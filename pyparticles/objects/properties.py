from random import random
import pygame
from pyparticles.engine. utils import Point, rand_iter

# TODO: add chained physics resolution, meaning particles will call `update()` on other
# update-able particles that are blocking thier movement. This will allow for cool things,
# such as entire piles of gravtity-affected particles falling at once or fluids flowing
# more smoothly. However, this will be difficult since we need to track which particles
# have been called in the resolution chain to prevent infinite loops and repeat work,
# but this tracking value must also be reset after each chain resolves

class BaseParticle(pygame.sprite.DirtySprite):
    """Base class for all other particles.

    Subclasses must assign `image` and `rect` attributes for the sprites to render properly.
    The inherited DirtySprite attributes may be overridden for specific behavior, but the
    default parameters work perfectly fine for most use.

    This is designed to be the superclass of many other cooperative subclasses. All subclasses
    of this will call `super().__init__()` within their `__init__()` functions. Once the
    initialization chain reaches this class, typical single-inheritence behavior takes over.

    Args:
        **kwargs (any): Variable length list of keyword arguments. The following keyword arguments
            are recognized:\n
            - groups (list): List of groups to add this sprite to. Defaults to None.

    Attributes:
        dirty (int): Indicates if this sprite is dirty. If so, it will be redrawn next frame.
            0 means the sprite is clean, 1 means it is dirty, and 2 means it is always dirty.
        prev_dirty (int): The dirty value of this sprite last frame.
        image (pygame.Surface): The image for this sprite.
        rect (pygame.Rect): The rectangle corresponding to the location and size of this sprite.
    """

    # dirty: int
    # image: pygame.Surface
    # rect: pygame.Rect

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'groups':
                pygame.sprite.DirtySprite.__init__(self, *value)
                return
        pygame.sprite.DirtySprite.__init__(self)
        # initialize attributes to default values (mostly to calm PyLint down)
        self.dirty = 1
        self.image = None
        self.rect = None

    def update(self, **kwargs):
        """Method to control sprite behavior.

        Default method does nothing. To implement specific behavior, it must be overridden by
        subclasses. These implementations should be prefaced by `if self.dirty != 0: pass` to
        prevent the particle from being updated multiple times per frame.
        """

class GravityArgs():
    def __init__(self, vec=(0,0), prob=1.0):
        self.vec = Point(vec)
        self.prob = prob

    def copy(self):
        return GravityArgs(vec=self.vec, prob=self.prob)

class GravityParticle(BaseParticle):
    """Particle with gravity (or any other kind of constant linear force)

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:\n
            - gravity (GravityArgs): GravityArgs object representing the direction and probability
                of this particle's gravity.
            - gravity_vec (Point, Point-like): X,Y vector representing the force to be applied
                to the particle. Defaults to (0, 0).
            - gravity_prob (float): Probablity (from 0.0 to 1.0) that the particle will update due to
                this property. Defaults to 1.0.

    Attributes:
        gravity (GravityArgs): The gravity vector and probability of the particle.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = GravityArgs()
        for key, value in kwargs.items():
            if key == 'gravity':
                self.gravity = value.copy()
            if key == 'gravity_vec':
                self.gravity.vec = Point(value)
            if key == 'gravity_prob':
                self.gravity.prob = value

    def update(self, **kwargs):
        if self.dirty != 0 or random() > self.gravity.prob:
            return
        sim = kwargs['sim']
        # apply gravity and clamp the new position
        pos = sim.get_pos(self.rect.topleft)
        new_pos = pos + self.gravity.vec
        new_pos = sim.clamp_pos(new_pos)
        # we can't move because we're at the edge of the sim
        if pos == new_pos:
            return
        # try to move to the new position
        # TODO: chained physics resolution
        dest = sim.get_cell(new_pos)
        if dest is None:
            sim.move_particle(self, new_pos)
            self.dirty = 1

class HeapArgs():
    def __init__(self, vec=None, prob=1.0, limit=None, stuck=False):
        self.vec = []
        if vec is not None:
            for p in vec:
                self.vec.append(Point(p))
        self.prob = prob
        self.limit = []
        if limit is not None:
            for p in limit:
                self.vec.append(Point(p))
        self.stuck = stuck

    def copy(self):
        return HeapArgs(vec=self.vec, prob=self.prob, limit=self.limit, stuck=self.stuck)

class HeapableParticle(BaseParticle):
    """Particle that can form heaps/piles.

    Does not inherit from GravityParticle, but subclasses must inherit from GravityParticle. To
    ensure ideal behavior, inherit from GravityParticle immediately before this, so particles will
    immediately try to form heaps is they cannot fall.

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:\n
            - heap_vec (list[Point], list[Point-like]): List of x,y vectors representing the
                directions this particle can move to form heaps. Defaults to [].
            - heap_prob (float): Probablity (from 0.0 to 1.0) that the particle will update due to
                this property. This can be thought of as the particle's 'friction'.
                Defaults to 1.0.
            - heap_limit (list[Point], list[Point-like]): List of x,y vectors that will force this
                particle to fall if any of them are empty. Defaults to [].
            - heap_stuck (bool): Whether or not

    Attributes:
        TODO
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heap = HeapArgs()
        for key, value in kwargs.items():
            if key == 'heap':
                self.heap = value.copy()
            if key == 'heap_vec':
                for p in value:
                    self.heap.vec.append(Point(p))
            if key == 'heap_prob':
                self.heap.prob = value
            if key == 'heap_limit':
                for p in value:
                    self.heap.limit.append(Point(p))
            if key == 'heap_stuck':
                self.heap.stuck = value

    def _move(self, sim, dest_pos):
        sim.move_particle(self, dest_pos)
        self.heap.stuck = False
        self.dirty = 1

    def update(self, **kwargs):
        if self.dirty != 0:
            return
        sim = kwargs['sim']
        # check if this particle is on top of another particle
        pos = sim.get_pos(self.rect.topleft)
        dest_cell = sim.get_cell(pos + self.gravity.vec)
        if dest_cell is None or dest_cell is self:
            return
        # check if this particle is at its heap limit
        for v in self.heap.limit:
            if sim.get_cell(pos + v) is None:
                vec = v.normalize()
                if sim.get_cell(pos + vec) is None:
                    self._move(sim, pos + vec)
                    return
        # check if the particle is stuck in place
        if self.heap.stuck:
            return
        # try to form a heap
        for heap_dir in rand_iter(self.heap.vec):
            new_pos = Point(pos + heap_dir)
            new_pos = sim.clamp_pos(new_pos)
            dest = sim.get_cell(new_pos)
            # move to an empty spot or get stuck
            if dest is None:
                if random() > self.heap.prob:
                    self.heap.stuck = True
                    return
                self._move(sim, new_pos)
                return
