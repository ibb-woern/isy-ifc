import json
import os
import xmltodict
from typing import List, Any, Dict

from models.manhole import Manhole
from models.sewer import Sewer
from data_types import resolver


def parse(file_path: os.PathLike) -> tuple:
    manholes: List[Manhole] = []
    sewers: List[Sewer] = []
    with open(file_path, "r", encoding="iso-8859-1") as f:
        xml_data = f.read()

    data = xmltodict.parse(xml_data)

    dt_resolver = resolver.DatatypeResolver()

    def deep_convert(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively iterates through a dictionary and converts data types."""
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                converted_data[key] = deep_convert(value)
            else:
                converted_data[key] = dt_resolver.resolve(key, value)
        return converted_data

    # Deep convert the parsed data
    converted_data = deep_convert(data)
    # encode the converted data to UTF-8
    # converted_data = converted_data.encode("utf-8")

    with open("converted_data.json", "w", encoding="utf8") as json_file:
        json.dump(converted_data, json_file, indent=2, ensure_ascii=False)

    return manholes, sewers
