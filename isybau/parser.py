import os
import re
import xmltodict
from typing import List, Any, Dict

from models.manhole import Manhole
from models.sewer import Sewer
from data_types import resolver


def detect_xml_encoding(file_path: os.PathLike) -> str:
    """Detect the encoding of an XML file by reading the first bytes.
    If the encoding is not found, default to UTF-8.
    """
    with open(file_path, "rb") as f:
        byte_data = f.read(100)  # Read the first 100 bytes

    xml_declaration = byte_data.decode("utf-8", errors="ignore")
    encoding_match = re.search(r'encoding="([^"]+)"', xml_declaration)
    if encoding_match:
        return encoding_match.group(1)
    else:
        return "utf-8"  # Default to UTF-8 if no encoding is found


def parse(file_path: os.PathLike) -> tuple:
    encoding = detect_xml_encoding(file_path)
    with open(file_path, "r", encoding=encoding) as f:
        xml_data = f.read()

    data = xmltodict.parse(xml_data)

    # Load datatypes extracted from xsd files
    dt_resolver = resolver.DatatypeResolver()

    def deep_convert(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively iterates through a dictionary and converts data types."""
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                # If the value is a dictionary, recursively convert it
                converted_data[key] = deep_convert(value)
            elif isinstance(value, list):
                # If the value is a list, process each item in the list
                converted_list = []
                for item in value:
                    if isinstance(item, dict):
                        # Recursively convert dictionaries within the list
                        converted_list.append(deep_convert(item))
                    else:
                        # Convert simple items in the list
                        converted_list.append(dt_resolver.resolve(key, item))
                converted_data[key] = converted_list
            else:
                # Convert simple values
                converted_data[key] = dt_resolver.resolve(key, value)
        return converted_data

    # Convert the data to the correct data types
    data = deep_convert(data)

    project: Dict = data["Identifikation"]["Admindaten"]
    manholes: List[Dict] = []
    sewers: List[Dict] = []
    for a in data["Identifikation"]["Datenkollektive"]["Stammdatenkollektiv"][
        "AbwassertechnischeAnlage"
    ]:
        if a["Objektart"] == "1":
            sewers.append(a)
            continue
        if a["Objektart"] == "2":
            manholes.append(a)
            continue

    """
    # For debugging purposes, write the converted data to a JSON file
    with open("data.json", "w", encoding="utf8") as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)
    """

    return project, manholes, sewers
