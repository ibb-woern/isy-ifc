import enum
import xmltodict
from lxml import etree as ET
from typing import Type, Union
from isybau.datatype_resolver import DatatypeResolver


def xml_get_tag_content(
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


def try_match_enum(value: str, enum_type: Type[enum.Enum]) -> Union[enum.Enum, None]:
    try:
        return enum_type(value)
    except ValueError:
        return None


def xml_element_to_dict(element: ET.Element) -> dict:
    xml = ET.tostring(element)
    data = xmltodict.parse(xml)

    if data["AbwassertechnischeAnlage"]:
        data = data["AbwassertechnischeAnlage"]

    resolver = DatatypeResolver()

    # Loop over the dict. Only the first level is currently supported.
    for key in data:
        data[key] = resolver.resolve(key, data[key])

    return data
