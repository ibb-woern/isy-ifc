from models.manhole import Manhole


class PipeSection:
    """Representing a pipe section in a sewer network.

    Attributes:
        start (Manhole): The start manhole of the pipe section.
        end (Manhole): The end manhole of the pipe section.
        diameter_inner (float): The inner diameter of the pipe section.
        diameter_outer (float, float): The outer diameter of the pipe section.
    """

    def __init__(
        self,
        start: Manhole,
        end: Manhole,
        diameter_inner: float,
        diameter_outer: float = None,
    ):
        self.start = start
        self.end = end
        self.diameter_inner = diameter_inner
        self.diameter_outer = diameter_outer
