import os
from typing import List, Union
import enum
from typing import Type

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from models.types import StatusType, SystemType, MaterialType
from models.manhole import Manhole


def _try_match_enum(value: str, enum_type: Type[enum.Enum]) -> Union[enum.Enum, None]:
    try:
        return enum_type(value)
    except ValueError:
        return None


def _create_row_dict(row, headers) -> dict:
    row_dict = {}
    i = 0
    for column in row:
        row_dict[headers[i]] = column
        i += 1
    return row_dict


def _manholes(ws: Worksheet) -> List[Manhole]:
    manholes = []
    headers = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    for row in ws.iter_rows(values_only=True, min_row=2):
        row_dict = _create_row_dict(row, headers)
        manhole = Manhole(
            name=row_dict["ID_CUR"],
            x=row_dict["POS_X"],
            y=row_dict["POS_Y"],
            z=row_dict["POS_Z"],
            z_top=row_dict["POS_DZ"],
            status=_try_match_enum(row_dict["STATUS.KZ"], StatusType),
            system=_try_match_enum(row_dict["TYP.KZ"], SystemType),
            form=row_dict["FORM.KZ"],
            coverplate=row_dict["COVERPLATE.KZ"],
            cone=row_dict["CONE.KZ"],
            nominal_length=row_dict["SIZE_A"],
            nominal_width=row_dict["SIZE_B"],
            material=_try_match_enum(row_dict["MATERIAL.KZ"], MaterialType),
        )
        manholes.append(manhole)
    return manholes


def parse(file_path: os.PathLike):
    wb = load_workbook(file_path, data_only=True)
    # iterate over sheets
    for ws in wb.worksheets:
        if ws.title == "schaechte":
            manholes = _manholes(ws)
            print(manholes[0])
        if ws.title == "haltungen":
            print("Haltungen are currently not yet supported")
        if ws.title == "leitungen":
            print("Leitungen are currently not yet supported")
        if ws.title == "strasseneinlaeufe":
            print("Strasseneinlaeufe are currently not yet supported")
        if ws.title == "hausanschluesse":
            print("Hausanschluesse are currently not yet supported")
        if ws.title == "bauwerke":
            print("Bauwerke are currently not yet supported")
