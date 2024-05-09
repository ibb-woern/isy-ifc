from dataclasses import dataclass
from typing import Optional
from lxml import etree as ET

from models.types import StatusType, SystemType, ManholeFormType, MaterialType
from isybau.lib import try_match_enum, xml_element_to_dict, xml_get_tag_content


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
        isybau_data (dict, optional): All data from the ISYBAU XML file.
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
    isybau_data: Optional[dict] = None

    def __post_init__(self):
        # Explicitly cast the name attribute to string to prevent later issues with the ifcopenshell root.create_entity function
        self.name = str(self.name)
        if not self.depth:
            if self.z and self.z_top:
                self.depth = self.z_top - self.z

        if self.depth and self.depth < 0:
            print(f"Manhole {self.name} has a negative depth.")
            self.depth = None

    @staticmethod
    def from_xml_element(
        element: ET.Element,
    ) -> "Manhole":  # "Manhole" is a forward reference to the class itself
        if element.find("Objektbezeichnung") is not None:
            name = element.find("Objektbezeichnung").text
        else:
            return

        points = []
        for point in element.iter("Punkt"):
            data = {
                "x": xml_get_tag_content(point, "Rechtswert", "float"),
                "y": xml_get_tag_content(point, "Hochwert", "float"),
                "z": xml_get_tag_content(point, "Punkthoehe", "float"),
                "type": xml_get_tag_content(point, "PunktattributAbwasser"),
            }
            points.append(data)

        x, y, z, z_top = None, None, None, None
        for point in points:
            if point["type"] == "SMP":
                x = point["x"]
                y = point["y"]
                z = point["z"]
            elif point["type"] == "DMP":
                z_top = point["z"]

        depth = xml_get_tag_content(element, "Schachttiefe", "float")
        if depth is None and z is not None and z_top is not None:
            depth = z_top - z

        status = xml_get_tag_content(element, "Status", "int")
        system = xml_get_tag_content(element, "Entwaesserungsart")

        form = xml_get_tag_content(element, "Aufbauform")
        if form is not None:
            form = xml_get_tag_content(element, "Unterteilform")

        coverplate = xml_get_tag_content(element, "Abdeckplatte", "bool")
        cone = xml_get_tag_content(element, "Konus", "bool")

        nominal_length = xml_get_tag_content(element, "LaengeUnterteil", "float")
        if nominal_length is None:
            nominal_length = xml_get_tag_content(element, "LaengeAufbau", "float")
        nominal_width = xml_get_tag_content(element, "BreiteUnterteil", "float")
        if nominal_width is None:
            nominal_width = xml_get_tag_content(element, "BreiteAufbau", "float")

        material = xml_get_tag_content(element, "MaterialUnterteil")
        if material is None:
            material = xml_get_tag_content(element, "MaterialAufbau")

        manhole = Manhole(
            name=name,
            x=x,
            y=y,
            z=z,
            z_top=z_top,
            depth=depth,
            status=try_match_enum(status, StatusType),
            system=try_match_enum(system, SystemType),
            form=try_match_enum(form, ManholeFormType),
            coverplate=coverplate,
            cone=cone,
            nominal_length=nominal_length,
            nominal_width=nominal_width,
            material=try_match_enum(material, MaterialType),
            isybau_data=xml_element_to_dict(element),
        )

        return manhole
