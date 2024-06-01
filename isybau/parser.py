import json
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
    manholes: List[Manhole] = []
    sewers: List[Sewer] = []

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
    converted_data = deep_convert(data)

    with open("converted_data.json", "w", encoding="utf8") as json_file:
        json.dump(converted_data, json_file, indent=2, ensure_ascii=False)

    return manholes, sewers
