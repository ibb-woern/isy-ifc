from dataclasses import dataclass
from typing import Optional

from models.types import StatusType, SystemType, ManholeFormType, MaterialType


@dataclass
class Manhole:
    """Representing a manhole in a sewer network.

    Attributes:
        name (str): The name of the manhole.
        x (float): The x-coordinate of the center.
        y (float): The y-coordinate of the center.
        z (float): The z-coordinate of the center on pipe level.
        z_top (float): The z-coordinate of the top of the manhole(cover).
        depth (float, optional): The depth of the manhole.
        status (StatusType, optional): The status of the manhole.
        system (SystemType, optional): The sewer system the manhole belongs to.
        form (ManholeFormType, optional): The form of the manhole.
        coverplate (bool, optional): Whether the manhole has a cover plate.
        cone (bool, optional): Whether the manhole has a cone.
        nominal_length (float, optional): Length of the manhole. For round manholes this is the diameter.
        nominal_width (float, optional): width of the manhole.
        material (MaterialType, optional): The material of the manhole.
    """

    name: str
    x: float
    y: float
    z: float
    z_top: float
    depth: Optional[float] = None
    status: Optional[StatusType] = None
    system: Optional[SystemType] = None
    form: Optional[ManholeFormType] = None
    coverplate: Optional[bool] = None
    cone: Optional[bool] = None
    nominal_length: Optional[float] = None
    nominal_width: Optional[float] = None
    material: Optional[MaterialType] = None

    def __post_init__(self):
        # Explicitly cast the name attribute to string to prevent later issues with the ifcopenshell root.create_entity function
        self.name = str(self.name)
        if not self.depth:
            if self.z and self.z_top:
                self.depth = self.z_top - self.z

        if self.depth and self.depth < 0:
            print(f"Manhole {self.name} has a negative depth.")
            self.depth = None
