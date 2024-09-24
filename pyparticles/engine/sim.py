import pygame

class ParticleSim():
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
        # create a sprite group for all the particles
        self.particle_group = pygame.sprite.LayeredDirty()

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
        if x < 0:
            x = 0
        elif x >= self._sim_width:
            x = self._sim_width
        if y < 0:
            y = 0
        elif y >= self._sim_height:
            y = self._sim_height
        return (x, y)

    def get_cell(self, pos):
        """Return the item held at a given grid position.

        Args:
            pos (tuple): The grid position to retrieve the value of.

        Returns:
            any: The particle located at the given grid position, or None if there's no particle
        """
        x, y = pos
        return self._sim_grid[y][x]

    def move_particle(self, particle, pos):
        """_summary_

        Args:
            particle (_type_): _description_
            pos (_type_): _description_
        """
        old_x, old_y = self.get_pos(particle.rect.topleft)
        self._sim_grid[old_y][old_x] = None
        new_x, new_y = pos
        self._sim_grid[new_y][new_x] = particle

    def get_pos(self, abs_pos):
        x, y = abs_pos
        return (x // self._cell_width, y // self._cell_height)

    def update(self, **kwargs):
        self.particle_group.update(**kwargs, sim=self)

    def add_particle(self, particle, pos):
        x, y = pos
        if self._sim_grid[y][x] is not None:
            return False
        self.particle_group.add(particle)
        self._sim_grid[y][x] = particle
        particle.topleft = self._get_abs_pos(pos)
