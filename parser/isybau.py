import os
import tempfile
from pathlib import Path
from lxml import etree as ET


def _remove_namespace(file: os.PathLike) -> os.PathLike:
    to_remove = [
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        'xmlns:xs="http://www.w3.org/2001/XMLSchema"',
        'xmlns="http://www.bfr-abwasser.de"',
    ]
    with open(file, "r") as file:
        data = file.read()
        for string in to_remove:
            data = data.replace(string, "")
    tmp_dir = Path(tempfile.gettempdir())
    tmp_file = tmp_dir / f"tmp_{file.name}"
    with open(tmp_file, "w") as file:
        file.write(data)
    return tmp_file


def parse(file_path: os.PathLike):
    tree = ET.parse(_remove_namespace(file_path))
    root = tree.getroot()
    for child in root:
        print(child.tag, child.attrib)
    for element in root.iter("AbwassertechnischeAnlage"):
        pass
