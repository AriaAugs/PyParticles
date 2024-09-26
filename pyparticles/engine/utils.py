def vec_to_ints(vec):
    """Convert a pygame.Vector2 into a tuple of 2 integers.

    Args:
        vec (pygame.Vector2): The vector to convert to a tuple.

    Returns:
        tuple: 2-integer tuple equivalent of the given vector.
    """
    return (int(vec.x), int(vec.y))

def clamp(value, min_val, max_val):
    """Clamp a value between a minimum and maximum value.

    Args:
        value (int, float): The value to clamp.
        min_val (int, float): The minimum value to clamp to.
        max_val (int, float): The maximum value to clamp to.

    Returns:
        int, float: The clamped value.
    """
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value
