from random import choice
from pygame import Vector2

def rand_iter(vals):
    """Iterate over a list (or other iterable) in a random order

    Args:
        vals (iterable): The item to iterate over in a random order

    Yields:
        any: The next item in the random iteration
    """
    temp = vals[:]
    while len(temp) > 0:
        ret = choice(temp)
        temp.remove(ret)
        yield ret

class Point():
    def __init__(self, x_val, y_val=None):
        self.x = 0
        self.y = 0
        if y_val is None:
            if isinstance(x_val, Point):
                self.x = x_val.x
                self.y = x_val.y
            elif isinstance(x_val, (list, tuple)):
                self.x, self.y = x_val
            elif isinstance(x_val, Vector2):
                self.x = int(x_val.x)
                self.y = int(x_val.y)
            else:
                raise ValueError(f'Expected tuple, list, or Vector2, but got {x_val}')
        else:
            self.x = int(x_val)
            self.y = int(y_val)

    def __add__(self, other):
        other = Point(other)
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        other = Point(other)
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        other = Point(other)
        return Point(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        other = Point(other)
        self.x -= other.x
        self.y -= other.y
        return self

    def __eq__(self, other):
        other = Point(other)
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        other = Point(other)
        return self.x < other.x and self.y < other.y

    def __gt__(self, other):
        other = Point(other)
        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        other = Point(other)
        return self < other or self == other

    def __ge__(self, other):
        other = Point(other)
        return self > other or self == other

    def __iter__(self):
        yield self.x
        yield self.y

    def clamp(self, min_point, max_point, exclude_min=False, exclude_max=True):
        min_point = Point(min_point)
        if exclude_min:
            min_point += (1, 1)
        max_point = Point(max_point)
        if exclude_max:
            max_point -= (1, 1)
        clamped_point = Point(self)
        if clamped_point.x <= min_point.x:
            clamped_point.x = min_point.x
        elif clamped_point.x >= max_point.x:
            clamped_point.x = max_point.x
        if clamped_point.y <= min_point.y:
            clamped_point.y = min_point.y
        elif clamped_point.y >= max_point.y:
            clamped_point.y = max_point.y
        return clamped_point

    def clamp_self(self, min_point, max_point, exclude_min=False, exclude_max=True):
        clamped_point = self.clamp(min_point, max_point, exclude_min, exclude_max)
        self.x = clamped_point.x
        self.y = clamped_point.y