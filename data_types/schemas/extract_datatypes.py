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
            # Skip non simple types
            if data_type.endswith("Type"):
                continue
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
            # Skip non simple types
            if data_type.endswith("Type"):
                continue
            element_data_types[name] = data_type

    return element_data_types


data_types = {}
script_dir = Path(__file__).resolve().parent
files = list(script_dir.glob("*.xsd"))

for file in files:
    file_data_types = parse_file(file)
    data_types.update(file_data_types)

patches = {
    "gYearMonth": "string",
    "token": "string",
    "gYear": "integer",
    "Time": "string",
}


for dt in data_types.items():
    if dt[1] in patches.keys():
        data_types[dt[0]] = patches[dt[1]]

# Useful for debugging
# distinct_data_types = set(data_types.values())


with open(Path(__file__).resolve().parent.parent / "data_types.json", "w") as f:
    json.dump(data_types, f, indent=4)
