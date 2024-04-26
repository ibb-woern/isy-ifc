import json
from pathlib import Path


class DatatypeResolver:
    data_types = {}

    def __init__(self) -> None:
        script_dir = Path(__file__).resolve().parent
        json_file = script_dir / "data_types.json"
        with open(json_file, "r") as file:
            self.data_types = json.load(file)

    def resolve(self, element_name: str, data) -> str:
        if element_name in self.data_types:
            dt = self.data_types[element_name]
            if dt == "integer":
                return int(data)
            elif dt == "decimal":
                return float(data)
            elif dt == "boolean":
                return bool(data)
        return str(data)
