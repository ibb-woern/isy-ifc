import json
import xmltodict
from pathlib import Path

"""
This function parses the XML file and extracts the element names and their data types.
The data types are stored in a dictionary where the key is the element name and the value is the data type.
Then the dictionary is stored in a JSON file.
Under normal circumstances this does not need to be run again.
"""


def parse_file(file_path: Path) -> dict:
    # For now skip certain files
    to_skip = ["metadaten", "zustandstaten"]
    if any(x in str(file_path) for x in to_skip):
        return {}

    element_data_types = {}

    with open(file_path, "r", encoding="ISO-8859-1") as f:
        xml_data = f.read()
        # remove "xsd:" substring
        xml_data = xml_data.replace("xsd:", "")

    data = xmltodict.parse(xml_data)

    # Process simpleTypes
    if "simpleType" in data["schema"]:
        for simple_type in data["schema"]["simpleType"]:
            element_data_types[simple_type["@name"]] = simple_type["restriction"][
                "@base"
            ]

    # Process complexTypes
    if "complexType" in data["schema"]:
        for complex_type in data["schema"]["complexType"]:
            # If name attribute ends with "Type" skip it, because it's defined in the simpleTypes
            if complex_type["@name"].endswith("Type"):
                continue
            if "sequence" in complex_type:
                for element in complex_type["sequence"]["element"]:
                    element_data_types[element["@name"]] = element["@type"]
            if "complexContent" in complex_type:
                for element in complex_type["complexContent"]["extension"]["sequence"][
                    "element"
                ]:
                    element_data_types[element["@name"]] = element["@type"]

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

with open(Path(__file__).resolve().parent.parent / "data_types.json", "w") as f:
    json.dump(data_types, f, indent=4)
