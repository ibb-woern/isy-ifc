import json
from lxml import etree as ET
from pathlib import Path

"""
This function parses the XML file and extracts the element names and their data types.
The data types are stored in a dictionary where the key is the element name and the value is the data type.
Then the dictionary is stored in a JSON file.
Under normal circumstances this does not need to be run again.
"""


def parse_file(file_path: Path) -> dict:
    # Parse the XML string
    root = ET.parse(file_path).getroot()

    # Dictionary to store element names and their data types
    element_data_types = {}
    for element in root.iter():
        name = None
        if element.tag == "{http://www.w3.org/2001/XMLSchema}element":
            name = element.attrib["name"]
        if name is None:
            continue
        # process elements which have the type directly attachted as attribute
        if "type" in element.attrib:
            data_type = element.attrib["type"].split(":")[-1]
            element_data_types[name] = data_type
            continue
        # Check if there is a child element simpleType
        if element.find("{http://www.w3.org/2001/XMLSchema}simpleType") is not None:
            # Get the data type from the child element
            data_type = (
                element.find("{http://www.w3.org/2001/XMLSchema}simpleType")
                .find("{http://www.w3.org/2001/XMLSchema}restriction")
                .attrib["base"]
                .split(":")[-1]
            )
            element_data_types[name] = data_type

    return element_data_types


data_types = {}
script_dir = Path(__file__).resolve().parent
files = [
    "1707-betriebsdaten.xsd",
    "1707-hydraulikdaten.xsd",
    "1707-metadaten.xsd",
    "1707-praesentationsdaten.xsd",
    "1707-referenzlisten.xsd",
    "1707-stammdaten.xsd",
    "1707-zustandsdaten.xsd",
]
for file in files:
    xml_file = script_dir / "schemas" / file
    file_data_types = parse_file(xml_file)
    data_types.update(file_data_types)

# This is to manually double check if there are custom datatypes missing
distinct_data_types = set(data_types.values())

patches = {
    "LagestufeType": "string",
    "HoehenstufeType": "string",
    "BehandlungsartType": "integer",
    "PunktattributAbwasserType": "string",
    "UntersuchungBodenType": "integer",
    "PraesentationsdatentypType": "string",
    "StammdatentypType": "string",
    "token": "string",
}

for dt in data_types.items():
    if dt[1] in patches.keys():
        data_types[dt[0]] = patches[dt[1]]

distinct_data_types = set(data_types.values())
print(distinct_data_types)

with open(script_dir / "data_types.json", "w") as f:
    json.dump(data_types, f, indent=4)
