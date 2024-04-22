import os
import tempfile
from pathlib import Path
from typing import List, Union
from lxml import etree as ET
from lxml import objectify
from models.manhole import Manhole
from ifc.common import try_match_enum, find_manhole_by_name
from models.pipe_section import PipeSection
from models.types import (
    ProfileType,
    StatusType,
    SystemType,
    ManholeFormType,
    MaterialType,
)


def _get_tag_content(
    element: ET.Element, tag: str, datatype: str = "str"
) -> Union[str, int, float, bool, None]:
    child = element.find(f".//{tag}")
    if child is not None:
        text_content = child.text
        if text_content is not None:
            if datatype == "float":
                return float(text_content)
            elif datatype == "int":
                return int(text_content)
            elif datatype == "bool":
                return bool(text_content)
            else:
                return text_content
    return None


def _remove_namespace(file: os.PathLike) -> os.PathLike:
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(file, parser)
    root = tree.getroot()

    for elem in root.getiterator():
        if not hasattr(elem.tag, "find"):
            continue  # guard for Comment tags
        i = elem.tag.find("}")
        if i >= 0:
            elem.tag = elem.tag[i + 1 :]
    objectify.deannotate(root, cleanup_namespaces=True)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = Path(temp_file.name)  # Convert to Path object
    temp_file_path = temp_file_path.parent / Path(file).name  # Append original filename
    tree.write(
        temp_file_path,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )
    return temp_file_path


def _parse_manhole(element: ET.Element):
    if element.find("Objektbezeichnung") is not None:
        name = element.find("Objektbezeichnung").text
    else:
        return

    points = []
    for point in element.iter("Punkt"):
        data = {
            "x": _get_tag_content(point, "Rechtswert", "float"),
            "y": _get_tag_content(point, "Hochwert", "float"),
            "z": _get_tag_content(point, "Punkthoehe", "float"),
            "type": _get_tag_content(point, "PunktattributAbwasser"),
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

    depth = _get_tag_content(element, "Schachttiefe", "float")
    if depth is None and z is not None and z_top is not None:
        depth = z_top - z

    status = _get_tag_content(element, "Status", "int")
    system = _get_tag_content(element, "Entwaesserungsart")

    form = _get_tag_content(element, "Aufbauform")
    if form is not None:
        form = _get_tag_content(element, "Unterteilform")

    coverplate = _get_tag_content(element, "Abdeckplatte", "bool")
    cone = _get_tag_content(element, "Konus", "bool")

    nominal_length = _get_tag_content(element, "LaengeUnterteil", "float")
    if nominal_length is None:
        nominal_length = _get_tag_content(element, "LaengeAufbau", "float")
    nominal_width = _get_tag_content(element, "BreiteUnterteil", "float")
    if nominal_width is None:
        nominal_width = _get_tag_content(element, "BreiteAufbau", "float")

    material = _get_tag_content(element, "MaterialUnterteil")
    if material is None:
        material = _get_tag_content(element, "MaterialAufbau")

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
    )

    return manhole


def _parse_pipe_section(element: ET.Element, manholes: List[Manhole]):
    if element.find("Objektbezeichnung") is not None:
        name = element.find("Objektbezeichnung").text
    else:
        return
    from_name = _get_tag_content(element, "KnotenZulauf")
    to_name = _get_tag_content(element, "KnotenAblauf")
    status = _get_tag_content(element, "Status", "int")
    system = _get_tag_content(element, "Entwaesserungsart")
    profile = _get_tag_content(element, "Profilart", "int")
    diameter_inner = _get_tag_content(element, "Profilbreite", "float")
    if diameter_inner:
        diameter_inner = diameter_inner / 1000  # Convert to meters
    diameter_outer = _get_tag_content(element, "Aussendurchmesser", "float")
    if diameter_outer:
        diameter_outer = diameter_outer / 1000
    material = _get_tag_content(element, "Material")

    pipe = PipeSection(
        name=name,
        start=find_manhole_by_name(from_name, manholes),
        end=find_manhole_by_name(to_name, manholes),
        status=try_match_enum(status, StatusType),
        system=try_match_enum(system, SystemType),
        profile=try_match_enum(profile, ProfileType),
        diameter_inner=diameter_inner,
        diameter_outer=diameter_outer,
        material=try_match_enum(material, MaterialType),
    )

    return pipe


def parse(file_path: os.PathLike) -> tuple:
    tree = ET.parse(_remove_namespace(file_path))
    root = tree.getroot()
    manholes: List[Manhole] = []
    sewers: List[PipeSection] = []
    # Maholes needs to be parsed first to map them in the pipe sections
    for element in root.iter("AbwassertechnischeAnlage"):
        objektart = int(element.find("Objektart").text)
        if objektart == 2:
            manhole = _parse_manhole(element)
            if manhole:
                manholes.append(manhole)

    for element in root.iter("AbwassertechnischeAnlage"):
        objektart = int(element.find("Objektart").text)
        if objektart == 1:
            sewer = _parse_pipe_section(element, manholes)
            if sewer:
                sewers.append(sewer)
    return manholes, sewers
