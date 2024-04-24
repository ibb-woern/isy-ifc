import enum
import xmltodict
from lxml import etree as ET
from typing import Type, Union


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

    return data
