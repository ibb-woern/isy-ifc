class Manhole:
    """Representing a manhole in a sewer network.

    Attributes:
        x (float): The x-coordinate of the center.
        y (float): The y-coordinate of the center.
        z (float): The z-coordinate of the center on pipe level.
        z_top (float): The z-coordinate of the top of the manhole(cover).
    """

    def __init__(self, x: float, y: float, z: float, z_top: float):
        self.x = x
        self.y = y
        self.z = z
        self.z_top = z_top
