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
        # Okay, this function doesn't *technically* do nothing, but this is just a sanity check
        # to handle any weird cases where this update function is called first in the MRO
        if self.dirty == 0:
            super().update(**kwargs)

    def move(self, sim, offset, condition=None):
        pass

class GravityArgs():
    def __init__(self, vec=(0,0), prob=1.0):
        self.vec = vec
        self.prob = prob

class GravityParticle(BaseParticle):
    """Particle with gravity (or any other kind of constant linear force)

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:\n
            - gravity_v (Vector2, Vector2 args): X,Y vector representing the force to be applied
                to the particle. Defaults to (0, 0).
            - gravity_p (float): Probablity (from 0.0 to 1.0) that the particle will update due to
                this property. Defaults to 1.0.

    Attributes:
        gravity_v (pygame.Vector2): 2-D vector representing the gravity applied to this particle.
        gravity_p (float): Probability that the particle will update due to this property.
    """

    # gravity: pygame.Vector2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity_v = pygame.Vector2(0, 0)
        self.gravity_p = 1.0
        for key, value in kwargs.items():
            if key == 'gravity_v':
                self._set_gravity_v(value)
            if key == 'gravity_p':
                self.gravity_p = value

    def _set_gravity_v(self, value):
        if isinstance(value, pygame.Vector2):
            self.gravity_v = value.copy()
        else:
            try:
                self.gravity_v = pygame.Vector2(value)
            except ValueError:
                print('ERROR: Could not set gravity value for particle')
                print('  Expected a Vector2 or Vector2 arguments')
                print(f'  Got: {value}')

    def update(self, **kwargs):
        if self.dirty != 0:
            return
        if random() > self.gravity_p:
            super().update(**kwargs)
            return
        sim = kwargs['sim']
        # apply gravity and clamp the new position
        pos = sim.get_pos(self.rect.topleft)
        new_pos = Point(pos + self.gravity_v)
        new_pos = sim.clamp_pos(new_pos)
        # if we can't move because we're at the edge, do nothing and call super().update()
        if pos == new_pos:
            super().update(**kwargs)
            return
        # try to move to the new position
        # TODO: chained physics resolution
        dest = sim.get_cell(new_pos)
        if dest is None:
            sim.move_particle(self, new_pos)
            self.dirty = 1

class HeapableParticle(BaseParticle):
    """Particle that can form heaps/piles.

    Does not inherit from GravityParticle, but subclasses must inherit from GravityParticle. To
    ensure ideal behavior, inherit from GravityParticle immediately before this, so particles will
    immediately try to form heaps is they cannot fall.

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:\n
            - heap_v (list[Vector2], list[Vector2 args]): List of x,y vectors representing the
                directions this particle can move to form heaps. Defaults to [].
            - heap_p (float): Probablity (from 0.0 to 1.0) that the particle will update due to
                this property. This can be thought of as the particle's 'friction'.
                Defaults to 1.0.

    Attributes:
        heap_v (pygame.Vector2): 2-D vector representing the gravity applied to this particle.
        heap_p (float): Probability that the particle will update due to this property.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heap_v = []
        self.heap_p = 1.0
        self.heap_g = [pygame.Vector2]
        for key, value in kwargs.items():
            if key == 'heap_v':
                self._set_heap_v(value)
            if key == 'heap_p':
                self.heap_p = value
        self.moved = False

    def _set_heap_v(self, value):
        for vec in value:
            if isinstance(vec, pygame.Vector2):
                self.heap_v.append(vec.copy())
            else:
                try:
                    self.heap_v.append(pygame.Vector2(vec))
                except ValueError:
                    print('ERROR: Could not set heap value for particle')
                    print('  Expected a Vector2 or Vector2 arguments')
                    print(f'  Got: {vec}')

    def update(self, **kwargs):
        if self.dirty != 0:
            print('Already been updated')
            return
        if self.prev_dirty == 0 or random() > self.heap_p:
            if self.moved:
                print(f'Not moving - prev_dirty = {self.prev_dirty}')
                self.moved = False
            #print(f'Dirty: {self.dirty}')
            super().update(**kwargs)
            return
        sim = kwargs['sim']
        # check that we're on top of another particle, according to this particle's gravity
        pos = sim.get_pos(self.rect.topleft)
        new_pos = Point(pos + self.gravity_v)
        new_pos = sim.clamp_pos(new_pos)
        dest = sim.get_cell(new_pos)
        if dest is None or dest is self:
            print(f'Dest is None: {dest is None}')
            super().update(**kwargs)
            return
        # try to form a heap
        # TODO: chained physics resolution
        for heap_dir in rand_iter(self.heap_v):
            new_pos = Point(pos + heap_dir)
            new_pos = sim.clamp_pos(new_pos)
            dest = sim.get_cell(new_pos)
            print(f'{new_pos} is {dest}')
            # move to an empty spot
            if dest is None:
                print('Moving to new {new_pos}')
                self.moved = True
                sim.move_particle(self, new_pos)
                self.dirty = 1
                return
