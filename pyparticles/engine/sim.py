import pygame
from pyparticles.engine import utils

class ParticleSim():
    """Self-contained particle simulation.

    On each call to `update()`, all particles in this simulation will be updated, then they will
    be drawn onto an image that spans the entire simulation. By encapsulating the simulation like
    this, it should be easier to change where the simulation is drawn within the program window
    and to apply pan/zoom to the final image displayed to the user.

    Args:
        sim_size (tuple): Grid size of the simulation.
        cell_size (tuple): Pixel size of each grid cell.
        bg_img (pygame.Surface): Background image for the simulation. Defaults to None.
        bg_clr (pygame.Color): Background color for the simulation. Defaults to None.

    Attributes:
        image (pygame.Surface): The image corresponding to the current simulation state.
    """

    image:pygame.Surface

    def __init__(self, sim_size, cell_size, bg_img=None, bg_clr=None):
        # break the sim size into width and height, then make a 2D array of that size
        self._sim_width, self._sim_height = sim_size
        self._sim_grid = [
            [None for x in range(self._sim_width)]
            for y in range(self._sim_height)]
        # break the cell size into width and height, then create a surface to draw the simulation
        # on. This surface will be big enough to draw the entire simulation on at 1x scale
        self._cell_width, self._cell_height = cell_size
        sim_size = (self._sim_width*self._cell_width, self._sim_height*self._cell_width)
        self.image = pygame.Surface(sim_size)
        # create a sprite group for all the particles and a list to track newly added particles
        self._particle_group = pygame.sprite.LayeredDirty()
        self._new_particles = []
        # set the background image that will be used when redrawing the sim
        bgd = None
        if bg_img is not None:
            bgd = pygame.transform.smoothscale(bg_img)
        elif bg_clr is not None:
            bgd = pygame.Surface(sim_size)
            bgd.fill(bg_clr)
        else:
            print('Using default black background for sim')
            bgd = pygame.Surface(sim_size)
            bgd.fill('black')
        self._particle_group.clear(self.image, bgd)

    def _get_abs_pos(self, pos):
        """Get the absolute/pixel position that corresponds to a given grid position.

        Args:
            pos (tuple): The grid position to translate to an absolute position.

        Returns:
            tuple: The absolute/grid position that corresponds to the given grid position.
        """
        x, y = pos
        return (x * self._cell_width, y * self._cell_height)

    def in_bounds(self, pos):
        """Check if a given grid position within the bounds of the grid.

        Args:
            pos (tuple): The grid position to check.

        Returns:
            bool: True if `pos` is in bounds, False otherwise.
        """
        x, y = pos
        return x < 0 or x >= self._sim_width or y < 0 or y >= self._sim_height

    def clamp_pos(self, pos):
        """Clamps a given grid position to be within bounds of the grid.

        Args:
            pos (tuple): The grid position to clamp.

        Returns:
            tuple: The clamped grid position.
        """
        x, y = pos
        x = utils.clamp(x, 0, self._sim_width-1)
        y = utils.clamp(y, 0, self._sim_height - 1)
        return (x, y)

    def get_cell(self, pos):
        """Return the item held at a given grid position.

        Args:
            pos (tuple): The grid position to retrieve the value of.

        Returns:
            pyparticles.properties.BaseParticle: The particle located at the given grid position.
            None: Returns `None` if there's no particle at the given grid position.
        """
        x, y = pos
        return self._sim_grid[y][x]

    def move_particle(self, particle, pos):
        """Moves a particle to a new grid position.

        Args:
            particle (pyparticles.properties.BaseParticle): The particle to move.
            pos (tuple): The grid position to move the particle to.
        """
        old_x, old_y = self.get_pos(particle.rect.topleft)
        self._sim_grid[old_y][old_x] = None
        new_x, new_y = pos
        self._sim_grid[new_y][new_x] = particle
        particle.rect.topleft = self._get_abs_pos(pos)

    def get_pos(self, abs_pos):
        """Get the grid position that corresponds to a given pixel position.

        Args:
            abs_pos (tuple): The pixel position to translate to a grid position.

        Returns:
            tuple: The grid position that corresponds to the given pixel position.
        """
        x, y = abs_pos
        return (x // self._cell_width, y // self._cell_height)

    def update(self, **kwargs):
        """Update the simulation by one step.

        This updates all the particles in the simulation and redraws the current sim state.
        Newly created/added particles won't be updated, but they will be drawn. This prevents
        an 'invisible' first update from occuring. The new particles then have their `dirty`
        attribute reset, since it doesn't reset automatically for some reason. This prevents
        them from being stuck for an extra frame.

        Args:
            **kwargs (any): Variable length list of keyword arguments. These arguments will be
                passed into each particle's `update()` function.
        """
        self._particle_group.update(**kwargs, sim=self)
        self._particle_group.draw(self.image)
        for p in self._new_particles:
            p.dirty = 0
        self._new_particles = []

    def add_particle(self, particle, pos):
        """Add a particle to the simulation at a given grid position.

        Newly added particles are added to a special list that gets cleared after each update.

        Args:
            particle (pyparticles.properties.BaseParticle): The particle to add.
            pos (tuple): The grid position to add the particle at.

        Returns:
            bool: True if the particle was added, False otherwise.
        """
        x, y = pos
        if self._sim_grid[y][x] is not None:
            return False
        self._particle_group.add(particle)
        self._sim_grid[y][x] = particle
        particle.rect.topleft = self._get_abs_pos(pos)
        self._new_particles.append(particle)
        return True
