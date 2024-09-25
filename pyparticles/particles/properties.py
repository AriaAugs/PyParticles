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

    This is designed to be the superclass of many other cooperative subclasses. All subclasses
    of this will call `super().__init__()` within their `__init__()` functions. Once the
    initialization chain reaches this class, typical single-inheritence behavior takes over.

    The following DirtySprite attributes may be overridden for specific behavior:
        - dirty (int): 0 for not dirty, 1 for dirty, 2 for always dirty. Defaults to 1.
        - blendmode (int): See the `special_flags` argument for `pygame.Surface.blit()`.
            Defaults to 0.
        - source_rect (pygame.Rect): Area of `self.image` to draw when rendering this sprite.
            Defaults to None.
        - visible (int): 0 for invisible, 1 for visible. Defaults to 1.
        - layer (int): Which layer to draw this sprite on. Defaults to 0.

    Args:
        **kwargs (any): Variable length list of keyword arguments. The following keyword arguments are
            recognized:
            - 'groups' (list): List of groups to add this sprite to. Defaults to None.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'groups':
                pygame.sprite.DirtySprite.__init__(self, *value)
                return
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1 # doesn't do anything besides getting PyLint to quiet down

    def update(self, **kwargs):
        """Method to control sprite behavior.

        Default method does nothing. To implement specific behavior, it must be overridden by
        subclasses. These implementations should be prefaced by `if self.dirty != 0: pass` to
        prevent the particle from being updated multiple times per frame.
        """


class GravityParticle(BaseParticle):
    """Particle with gravity (or any other kind of constant linear force)

    Args:
        **kwargs: Variable length list of keyword arguments. The following keyword arguments are
            recognized:
            - 'gravity' (Vector2, Vector2 args): X,Y vector representing the force to be applied
                to the particle. Defaults to (0, 0).
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
        pos = sim.get_pos(self.topleft)
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
