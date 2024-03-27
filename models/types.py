from enum import Enum


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1702252
# Translation based on https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcDistributionSystemEnum.htm
class SystemType(Enum):
    STORMWATER = "KR"
    WASTEWATER = "KS"
    SEWAGE = "KM"
    RAINWATER = "KW"
    STORMWATER_PUMPING = "DR"
    WASTEWATER_PUMPING = "DS"
    SEWAGE_PUMPING = "DM"
    STORMWATER_TRENCH = "GR"
    WASTEWATER_TRENCH = "GS"
    SEWAGE_TRENCH = "GM"
    RAINWATER_TRENCH = "GW"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1702349
class MaterialType(Enum):
    ASBESTOS_CEMENT = "AZ"
    CONCRETE = "B"
    CONCRETE_SEGMENTS = "BS"
    STAINLESS_STEEL = "CNS"
    UNIDENTIFIED_IRON_AND_STEEL = "EIS"
    FIBER_CEMENT = "FZ"
    GLASS_FIBER_REINFORCED_PLASTIC = "GFK"
    GREY_CAST_IRON = "GG"
    DUCTILE_CAST_IRON = "GGG"
    UNIDENTIFIED_PLASTIC = "KST"
    MASONRY = "MA"
    IN_SITU_CONCRETE = "OB"
    DRAIN_CONCRETE = "P"
    POLYMER_CONCRETE = "PC"
    POLYMER_MODIFIED_CEMENT_CONCRETE = "PCC"
    POLYETHYLENE = "PE"
    HIGH_DENSITY_POLYETHYLENE = "PEHD"
    POLYESTER_RESIN = "PH"
    POLYESTER_CONCRETE = "PHB"
    POLYPROPYLENE = "PP"
    POLYVINYL_CHLORIDE = "PVC"
    POLYVINYL_CHLORIDE_HARD = "PVCU"
    STEEL_FIBER_CONCRETE = "SFB"
    PRESTRESSED_CONCRETE = "SPB"
    REINFORCED_CONCRETE = "SB"
    STEEL = "ST"
    STONEWARE = "STZ"
    SPRAYED_CONCRETE = "SZB"
    UNIDENTIFIED_MATERIAL = "W"
    BRICKWORKS = "ZG"
    MIXED_MATERIALS = "MIX"
    UNPAVED_GROUND = "BOD"
    GRASS = "RAS"
    PAVING_STONE = "PFL"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1702900
# Translation based on https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/PEnum_ElementStatus.htm
class StatusType(Enum):
    EXISTING = 0
    NEW = 1
    FICTIONAL = 2
    DEMOLISH = 3
    DAMMED = 4
    OTHER = 5
    DISMANTLED = 6


class EdgeType(Enum):
    INLET = 0
    OUTLET = 1
    OTHER = 2


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1703837
class ProfileType(Enum):
    CIRCULAR = 0
    EGG_SHAPED = 1
    THROAT = 2
    RECTANGULAR_CLOSED = 3
    DOUBLE_WALL_CIRCULAR = 4
    RECTANGULAR_OPEN = 5
    EGG_SHAPED_DIFFERENT = 6
    THROAT_DIFFERENT = 7
    TRAPEZOIDAL = 8
    DOUBLE_TRAPEZOIDAL = 9
    U_SHAPED = 10
    ARCH_SHAPED = 11
    OVAL = 12
    OTHER = 13


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1703934
# Translation based on https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcPipeFittingTypeEnum.htm
class ConnectionFittingType(Enum):
    JUNCTION = "A"
    ENTRY = "S"
    JUNCTION_CLOSED = "AG"
    ENTRY_CLOSED = "SG"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704010
class NodeType(Enum):
    MANHOLE = 0
    CONNECTION = 1  # Anschlusspunkt
    STRUCTURE = 2  # Bauwerk


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704140
class CoverType(Enum):
    ROUND = "R"
    ROUND_BOLTED = "RV"
    RECTANGULAR = "E"
    RECTANGULAR_BOLTED = "EV"
    OTHER = "Z"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704284
class ManholeFormType(Enum):
    CIRCULAR = "R"
    RECTANGULAR = "E"
    OTHER = "Z"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704428
class ManholeBaseFormType(Enum):
    CIRCULAR = "R"
    RECTANGULAR = "E"
    WITHOUT = "O"  # z.B. Tangentialschacht
    OTHER = "Z"


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704472
class ChuteType(Enum):
    CIRCULAR_IMPOST = 0  # Kreis bis Kämpfer
    CIRCULAR_APEX = 1  # Kreis bis Scheitel
    RECTANGULAR_IMPOST = 2  # Rechteck bis Kämpfer
    RECTANGULAR_APEX = 3  # Rechteck bis Scheitel
    CLOSED_CHUTE = 4  # geschlossenes Gerinne
    SHOOT = 5  # Schussrinne
    CASCADE = 6  # Kaskade
    OTHER = 9


# Based on https://www.bfr-abwasser.de/html/A7-8-2Stammdaten.html#1704540
class ConnectionPointType(Enum):
    GENERAL = "AP"
    GUTTER = "ER"
    BUILDING = "GA"
    DOWNPIPE = "RR"
    INLET = "SE"
    UNKNOWN = "NN"
    RAINWATER_UTILIZATION = "AV"
    PIPE_END_CLOSED = "RV"
    PIPE_END_BUILDING = "EG"
    FLOOR_DRAIN = "BA"
    TRENCH_INFLOW = "ZG"
    DRAINAGE_BEGINNING = "DR"
    TRENCH_POINT = "GP"
    EXTERNAL_DIVERSION = "AS"  # not sure about that "Außenliegender Untersturz"
