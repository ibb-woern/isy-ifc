import math
import numpy
from models.manhole import Manhole
from models.types import ManholeFormType, ProfileType
from models.pipe_section import PipeSection
import ifcopenshell
from ifcopenshell.api import run
from ifc.common import assign_container, find_profile, extrusion_rotation_angles


def manhole(manhole: Manhole, model, context):
    # First check if all relevant information is available
    if not manhole.x or not manhole.y or not manhole.z or not manhole.z_top:
        return
    if not manhole.nominal_length:
        return
    if not manhole.form:
        return

    # Check if shape is round or rectangular
    profile = None
    if manhole.form == ManholeFormType.RECTANGULAR:
        if not manhole.nominal_width:
            manhole.nominal_width = manhole.nominal_length  # assume its a square
        profile_name = f"{round(manhole.nominal_length * 1000)}x{round(manhole.nominal_width * 1000)}"
        profile = find_profile(model, profile_name)
        if not profile:
            profile = model.create_entity(
                "IfcRectangleProfileDef",
                ProfileName=profile_name,
                ProfileType="AREA",
                XDim=manhole.nominal_length,
                YDim=manhole.nominal_width,
            )
    if manhole.form == ManholeFormType.CIRCULAR:
        profile_name = f"DN{round(manhole.nominal_length * 1000)}"
        profile = find_profile(model, profile_name)
        if not profile:
            profile = model.create_entity(
                "IfcCircleProfileDef",
                ProfileName=profile_name,
                ProfileType="AREA",
                Radius=manhole.nominal_length / 2,
            )
    # Skip for currently not supported profiles
    if not profile:
        return

    # Create the IFC entity
    manhole_entity = run(
        "root.create_entity",
        model,
        ifc_class="IfcDistributionChamberElement",
        name=manhole.name,
    )
    # Assign the entity to the tree
    assign_container(model, manhole_entity)

    # Set the placement of the manhole
    matrix = numpy.eye(4)
    matrix[:, 3][0:3] = (manhole.x, manhole.y, manhole.z)
    run(
        "geometry.edit_object_placement",
        model,
        product=manhole_entity,
        matrix=matrix,
    )

    # Add the profile representation to the manhole and assign it
    representation = run(
        "geometry.add_profile_representation",
        model,
        context=context,
        profile=profile,
        depth=manhole.depth,
    )
    run(
        "geometry.assign_representation",
        model,
        product=manhole_entity,
        representation=representation,
    )


def sewer(sewer: PipeSection, model, context):
    # Skip if start or end manhole is missing
    if not sewer.start or not sewer.end:
        return

    profile = None
    if sewer.profile == ProfileType.CIRCULAR:
        profile_name = f"DN{round(sewer.diameter_inner * 1000)}"
        profile = find_profile(model, profile_name)
        if not profile:
            wall_thickness = 0.01  # default wall thickness
            if sewer.diameter_outer:
                wall_thickness = sewer.diameter_outer - sewer.diameter_inner
            profile = model.create_entity(
                "IfcCircleHollowProfileDef",
                ProfileName=profile_name,
                ProfileType="AREA",
                Radius=sewer.diameter_inner / 2,
                WallThickness=wall_thickness,
            )
    # Skip for currently not supported profiles
    if not profile:
        return

    # Create the IFC entity
    sewer_entity = run(
        "root.create_entity",
        model,
        ifc_class="IfcPipeSegment",
        name=sewer.name,
    )
    assign_container(model, sewer_entity)

    # Calculate the length of the sewer and extrude using pythagoras.
    length = math.sqrt(
        (sewer.start.x - sewer.end.x) ** 2
        + (sewer.start.y - sewer.end.y) ** 2
        + (sewer.start.z - sewer.end.z) ** 2
    )
    matrix = numpy.eye(4)

    rotation_x, rotation_y = extrusion_rotation_angles(
        [sewer.start.x, sewer.start.y, sewer.start.z],
        [sewer.end.x, sewer.end.y, sewer.end.z],
    )

    matrix = ifcopenshell.util.placement.rotation(rotation_x, "X") @ matrix
    matrix = ifcopenshell.util.placement.rotation(rotation_y, "Y") @ matrix

    # now change the identity matrix to match the start point and rotation
    matrix[:, 3][0:3] = (sewer.start.x, sewer.start.y, sewer.start.z)

    run(
        "geometry.edit_object_placement",
        model,
        product=sewer_entity,
        matrix=matrix,
    )
    representation = run(
        "geometry.add_profile_representation",
        model,
        context=context,
        profile=profile,
        depth=length,
    )
    run(
        "geometry.assign_representation",
        model,
        product=sewer_entity,
        representation=representation,
    )
