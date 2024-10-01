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
        image (pygame.Surface): The image for this sprite.
        rect (pygame.Rect): The rectangle corresponding to the location and size of this sprite.
        updateable (bool): Whether or not this particle can update itself, assuming all
            probabilistic behavior triggers.
        dependants (list[BaseParticle]): Particles that can interact with this particle when active
        active (bool): active state of particle
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
        self.updateable = True
        self._dependants = []
        self.active = True
        self._depends_on = []
        self._updateable = True

    def add_dependant(self, particle):
        self._dependants.append(particle)

    def activate(self):
        self.active = True
        while len(self._dependants) > 0:
            self._dependants.pop().active = True
            # TODO: once we have chained physics resolution, call activate() on dependant cells
            #self._dependants.pop().activate()
        # TODO: some way to call update() to update particles on same frame they were activated on?

    def pre_update(self):
        self._updateable = False

    def update(self, **kwargs):
        """Method to control sprite behavior.

        Default method does nothing. To implement specific behavior, it must be overridden by
        subclasses. These implementations should be prefaced by `if self.dirty != 0: pass` to
        prevent the particle from being updated multiple times per frame.
        """
        if self.dirty != 0 or self._updateable:
            # TODO: make sure we wanna call `self.activate()`` here
            self.activate()
            return
        sim = kwargs['sim']
        pos = sim.get_pos(self.rect.topleft)
        for d in self._depends_on:
            p = sim.get_cell(pos + d)
            if p is not None:
                p.add_dependant(self)
        self.active = False

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
        self._depends_on.append(self.gravity.vec)

    def update(self, **kwargs):
        if self.dirty != 0:
            return
        sim = kwargs['sim']
        # apply gravity and clamp the new position
        dest_pos = sim.get_pos(self.rect.topleft) + self.gravity.vec
        # we can't move because we're at the edge of the sim
        if not sim.in_bounds(dest_pos):
            return
        # try to move to the new position
        # TODO: chained physics resolution
        dest_cell = sim.get_cell(dest_pos)
        if dest_cell is None: # particle can move
            if random() < self.gravity.prob:
                sim.move_particle(self, dest_pos)
                self.dirty = 1
            else: # particle failed random check, but could've moved
                self._updateable = True
            return
        # particle is blocked - cehck if blocking particle is active
        if dest_cell.active:
            self._updateable = True

class HeapArgs():
    def __init__(self, vecs=None, prob=1.0, limits=None, stuck=False):
        self.vecs = []
        if vecs is not None:
            for v in vecs:
                self.vecs.append(Point(v))
        self.prob = prob
        self.limits = []
        if limits is not None:
            for v in limits:
                self.limits.append(Point(v))
        self.stuck = stuck

    def copy(self):
        return HeapArgs(vecs=self.vecs, prob=self.prob, limits=self.limits, stuck=self.stuck)

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
                    self.heap.vecs.append(Point(p))
            if key == 'heap_prob':
                self.heap.prob = value
            if key == 'heap_limit':
                for p in value:
                    self.heap.limits.append(Point(p))
            if key == 'heap_stuck':
                self.heap.stuck = value
        if self.heap.vecs is not None and self.heap.prob >= 1.0:
            self._depends_on.extend(self.heap.vecs)
        if self.heap.limits is not None:
            self._depends_on.extend(self.heap.limits)

    def _move(self, sim, dest_pos):
        sim.move_particle(self, dest_pos)
        self.heap.stuck = False
        self.dirty = 1

    def update(self, **kwargs):
        if self.dirty != 0:
            return
        sim = kwargs['sim']
        limit_triggered = False
        # check if this particle is on top of another particle
        pos = sim.get_pos(self.rect.topleft)
        dest_pos = pos + self.gravity.vec
        if sim.in_bounds(dest_pos) and sim.get_cell(dest_pos) is None:
            return
        # check if this particle is at its heap limit
        for lim_vec in rand_iter(self.heap.limits):
            dest_pos = pos + lim_vec
            if not sim.in_bounds(dest_pos):
                continue
            if sim.get_cell(dest_pos) is None:
                dest_pos = pos + lim_vec.get_normalized()
                if not sim.in_bounds(dest_pos):
                    continue
                dest_cell = sim.get_cell(dest_pos)
                if dest_cell is None:
                    self._move(sim, dest_pos)
                    return
                limit_triggered = True
                self._updateable |= dest_cell.active
        # check if the particle is stuck in place
        if self.heap.stuck or limit_triggered:
            return
        # try to form a heap
        for heap_vec in rand_iter(self.heap.vecs):
            dest_pos = pos + heap_vec
            if not sim.in_bounds(dest_pos):
                continue
            dest_cell = sim.get_cell(dest_pos)
            if dest_cell is None:
                if random() >= self.heap.prob:
                    self.heap.stuck = True
                    return
                self._move(sim, dest_pos)
                return
            if self.heap.prob >= 1.0:
                self._updateable |= dest_cell.active