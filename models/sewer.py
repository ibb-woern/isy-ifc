from dataclasses import dataclass
from lxml import etree as ET
from typing import List, Optional
from ifc.shared import find_manhole_by_name
from models.manhole import Manhole
from models.types import ProfileType, StatusType, SystemType
from models.types import MaterialType
from isybau.lib import try_match_enum, xml_element_to_dict, xml_get_tag_content


@dataclass
class Sewer:
    """Representing a section in a sewer network.

    Attributes:
        name (str): The name of the sewer.
        start (Manhole): The start manhole of the sewer.
        end (Manhole): The end manhole of the sewer.
        x_1 (Optional[float]): X-coordinate of an alternative start point (not implemented).
        y_1 (Optional[float]): Y-coordinate of an alternative start point (not implemented).
        z_1 (Optional[float]): Z-coordinate of an alternative start point (not implemented).
        x_2 (Optional[float]): X-coordinate of an alternative end point (not implemented).
        y_2 (Optional[float]): Y-coordinate of an alternative end point (not implemented).
        z_2 (Optional[float]): Z-coordinate of an alternative end point (not implemented).
        status (Optional[StatusType]): The status of the sewer (default: None).
        system (Optional[SystemType]): The sewer system the sewer belongs to (default: None).
        profile (ProfileType): The profile type of the sewer (default: ProfileType.CIRCULAR).
        diameter_inner (float): The inner diameter of the sewer.
        diameter_outer (Optional[float]): The outer diameter of the sewer (default: None).
        material (Optional[MaterialType]): The material of the sewer (default: None).
        isybau_data (Optional[dict]): All data from the ISYBAU XML file (default: None).
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
    status: Optional[StatusType] = None
    system: Optional[SystemType] = None
    profile: ProfileType = ProfileType.CIRCULAR
    diameter_inner: float = None
    diameter_outer: Optional[float] = None
    material: Optional[MaterialType] = None
    isybau_data: Optional[dict] = None

    @staticmethod
    def from_xml_element(element: ET.Element, manholes: List[Manhole]):
        if element.find("Objektbezeichnung") is not None:
            name = element.find("Objektbezeichnung").text
        else:
            return
        from_name = xml_get_tag_content(element, "KnotenZulauf")
        to_name = xml_get_tag_content(element, "KnotenAblauf")
        status = xml_get_tag_content(element, "Status", "int")
        system = xml_get_tag_content(element, "Entwaesserungsart")
        profile = xml_get_tag_content(element, "Profilart", "int")
        diameter_inner = xml_get_tag_content(element, "Profilbreite", "float")
        if diameter_inner:
            diameter_inner = diameter_inner / 1000  # Convert to meters
        diameter_outer = xml_get_tag_content(element, "Aussendurchmesser", "float")
        if diameter_outer:
            diameter_outer = diameter_outer / 1000
        material = xml_get_tag_content(element, "Material")

        pipe = Sewer(
            name=name,
            start=find_manhole_by_name(from_name, manholes),
            end=find_manhole_by_name(to_name, manholes),
            status=try_match_enum(status, StatusType),
            system=try_match_enum(system, SystemType),
            profile=try_match_enum(profile, ProfileType),
            diameter_inner=diameter_inner,
            diameter_outer=diameter_outer,
            material=try_match_enum(material, MaterialType),
            isybau_data=xml_element_to_dict(element),
        )

        return pipe
