import os
import tempfile
from pathlib import Path
from typing import List
from lxml import etree as ET
from lxml import objectify
from models.manhole import Manhole
from models.sewer import Sewer


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


def parse(file_path: os.PathLike) -> tuple:
    tree = ET.parse(_remove_namespace(file_path))
    root = tree.getroot()
    manholes: List[Manhole] = []
    sewers: List[Sewer] = []
    # Maholes needs to be parsed first to map them in the pipe sections
    for element in root.iter("AbwassertechnischeAnlage"):
        objektart = int(element.find("Objektart").text)
        if objektart == 2:
            manhole = Manhole.from_xml_element(element)
            if manhole:
                manholes.append(manhole)

    for element in root.iter("AbwassertechnischeAnlage"):
        objektart = int(element.find("Objektart").text)
        if objektart == 1:
            sewer = Sewer.from_xml_element(element, manholes)
            if sewer:
                sewers.append(sewer)
    return manholes, sewers
