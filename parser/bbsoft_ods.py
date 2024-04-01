import os
import polars as pl
from typing import List, Tuple
import enum
from typing import Type, Union

from models.types import StatusType, SystemType, MaterialType
from models.manhole import Manhole


def _try_match_enum(value: str, enum_type: Type[enum.Enum]) -> Union[enum.Enum, None]:
    try:
        return enum_type(value)
    except ValueError:
        return None


def _manholes(df: pl.DataFrame) -> List[Manhole]:
    manholes = []
    for row in df.rows(named=True):
        manhole = Manhole(
            name=row["ID_CUR"],
            x=row["POS_X"],
            y=row["POS_Y"],
            z=row["POS_Z"],
            z_top=row["POS_DZ"],
            status=_try_match_enum(row["STATUS.KZ"], StatusType),
            system=_try_match_enum(row["TYP.KZ"], SystemType),
            form=row["FORM.KZ"],
            coverplate=row["COVERPLATE.KZ"],
            cone=row["CONE.KZ"],
            nominal_length=row["SIZE_A"],
            nominal_width=row["SIZE_B"],
            material=_try_match_enum(row["MATERIAL.KZ"], MaterialType),
        )
        manholes.append(manhole)
    return manholes


def _create_dataframes(file_path: os.PathLike) -> Tuple[pl.DataFrame]:
    pl.read_ods(file_path)
    sheet_names = ["schaechte", "haltungen"]
    # Also available, but not yet supported:
    # sheet_names = ["schaechte", "haltungen", "leitungen", "strasseneinlaeufe", "hausanschluesse", "bauwerke"]

    dfs = {}
    pl.Config.set_verbose(True)
    for sheet_name in sheet_names:
        try:
            dfs[sheet_name] = pl.read_ods(file_path, sheet_name=sheet_name)
        except pl.errors.PolarsError:
            print(f"Sheet {sheet_name} not found in {file_path}")

    print(dfs["schaechte"].head())
    exit()
    return dfs


def _sewers(df: pl.DataFrame):
    """
    name: str
    start: Manhole
    end: Manhole
    x_1: Optional[float] = None
    y_1: Optional[float] = None
    z_1: Optional[float] = None
    x_2: Optional[float] = None
    y_2: Optional[float] = None
    z_2: Optional[float] = None
    profile: ProfileType = ProfileType.CIRCULAR
    diameter_inner: float
    diameter_outer: Optional[float] = None
    material: Optional[MaterialType] = None
    """
    pass


def parse(file_path: os.PathLike):
    dfs = _create_dataframes(file_path)
    if "schaechte" in dfs:
        print(_manholes(dfs["schaechte"]))
