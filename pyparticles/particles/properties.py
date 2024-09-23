import pygame

class BaseParticle(pygame.sprite.DirtySprite):
    """Base class for all other particles.

    Subclasses must assign `image` and `rect` attributes for the sprites to render properly.

    The following DirtySprite attributes may be overridden for specific behavior:
        - dirty (int): 0 for not dirty, 1 for dirty, 2 for always dirty. Defaults to 1.
        - blendmode (int): See the `special_flags` argument for `pygame.Surface.blit()`.
            Defaults to 0.
        - source_rect (pygame.Rect): Area of `self.image` to draw when rendering this sprite.
            Defaults to None.
        - visible (int): 0 for invisible, 1 for visible. Defaults to 1.
        - layer (int): Which layer to draw this sprite on. Defaults to 0.

    Args:
        *groups: Variable length list of groups to add this sprite to.

    """

    def __init__(self, *groups):
        pygame.sprite.DirtySprite.__init__(self, groups)
        self._locked = False

    def update(self):
        """Method to control sprite behavior.

        Default method does nothing. To implement specific behavior, it must be overridden
        by subclasses. However, the `if self.dirty != 0` check included in the default
        implementation is important to carry over to prevent particles from being updated
        multiple times per frame (due to other particles interacting with this particle)
        """
        if self.dirty != 0:
            pass
