from dataclasses import dataclass
from typing import Optional
from models.manhole import Manhole
from models.types import ProfileType
from models.types import MaterialType


@dataclass
class PipeSection:
    """Representing a pipe section in a sewer network.

    Attributes:
        name (str): The name of the pipe section.
        start (Manhole): The start manhole of the pipe section.
        end (Manhole): The end manhole of the pipe section.
        x_1 (Optional[float]): X-coordinate of an alternative start point (not implemented).
        y_1 (Optional[float]): Y-coordinate of an alternative start point (not implemented).
        z_1 (Optional[float]): Z-coordinate of an alternative start point (not implemented).
        x_2 (Optional[float]): X-coordinate of an alternative end point (not implemented).
        y_2 (Optional[float]): Y-coordinate of an alternative end point (not implemented).
        z_2 (Optional[float]): Z-coordinate of an alternative end point (not implemented).
        profile (ProfileType): The profile type of the pipe section (default: ProfileType.CIRCULAR).
        diameter_inner (float): The inner diameter of the pipe section.
        diameter_outer (Optional[float]): The outer diameter of the pipe section (default: None).
        material (Optional[MaterialType]): The material of the pipe section (default: None).
    """

    name: str
    start: Manhole
    end: Manhole
    x_1: Optional[float] = None
    y_1: Optional[float] = None
    z_1: Optional[float] = None
    x_2: Optional[float] = None
    y_2: Optional[float] = None
    z_2: Optional[float] = None
    profile: ProfileType = ProfileType.CIRCULAR
    diameter_inner: float
    diameter_outer: Optional[float] = None
    material: Optional[MaterialType] = None
