import pygame
from pyparticles.engine import utils
from pyparticles.engine import sim as simulation

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
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'groups':
                pygame.sprite.DirtySprite.__init__(self, *value)
                return
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1 # doesn't do anything besides making PyLint quiet down

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


class GravityParticle(BaseParticle):
    """Particle with gravity (or any other kind of constant linear force)

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:\n
            - gravity (Vector2, Vector2 args): X,Y vector representing the force to be applied
                to the particle. Defaults to (0, 0).

    Attributes:
        gravity (pygame.Vector2): 2-D vector representing the gravity applied to this particle.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = pygame.Vector2(0, 0)
        for key, value in kwargs.items():
            if key == 'gravity':
                if isinstance(value, pygame.Vector2):
                    self.gravity = value.copy()
                else:
                    try:
                        self.gravity = pygame.Vector2(value)
                    except ValueError:
                        print('ERROR: Could not set gravity value for particle')
                        print('  Expected a Vector2 or Vector2 arguments')
                        print(f'  Got: {value}')

    def update(self, **kwargs):
        if self.dirty != 0:
            return
        # apply gravity and clamp the new position
        sim: simulation.ParticleSim = kwargs['sim']
        pos = sim.get_pos(self.rect.topleft)
        new_pos = utils.vec_to_ints(pos + self.gravity)
        new_pos = sim.clamp_pos(new_pos)
        # if we can't move because we're at the edge, do nothing and call super().update()
        if pos == new_pos:
            super().update(**kwargs)
            return
        # check if we can move to the position, otherwise check if the blocking particle can move
        dest = sim.get_cell(new_pos)
        if dest is None:
            sim.move_particle(self, new_pos)
            self.dirty = 1
