class Manhole:
    """Representing a manhole in a sewer network.

    Attributes:
        name (str): The name of the manhole.
        x (float): The x-coordinate of the center.
        y (float): The y-coordinate of the center.
        z (float): The z-coordinate of the center on pipe level.
        z_top (float): The z-coordinate of the top of the manhole(cover).
    """

    def __init__(self, name: str, x: float, y: float, z: float, z_top: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.z_top = z_top
