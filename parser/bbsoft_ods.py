import os
import polars as pl


def parse(file_path: os.PathLike):
    pl.read_ods(file_path)
    sheet_names = ["schaechte", "haltungen", "leitungen"]

    dfs = {}
    for sheet_name in sheet_names:
        try:
            dfs[sheet_name] = pl.read_ods(file_path, sheet_name=sheet_name)
        except pl.errors.PolarsError:
            print(f"Sheet {sheet_name} not found in {file_path}")

    """
    name: str
    x: float
    y: float
    z: float
    z_top: float
    status: Optional[str] = None
    system: Optional[str] = None
    form: Optional[str] = None
    coverplate: Optional[bool] = None
    cone: Optional[bool] = None
    size_a: Optional[float] = None
    size_b: Optional[float] = None
    material: Optional[str] = None

    """
