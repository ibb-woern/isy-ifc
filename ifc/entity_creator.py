import numpy
from models.manhole import Manhole
from models.types import ManholeFormType, ProfileType
from models.pipe_section import PipeSection
from ifcopenshell.api import run
from ifc.common import find_profile, assign_container


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
    profile = None
    if sewer.profile == ProfileType.CIRCULAR:
        profile_name = f"DN{round(sewer.diameter_inner * 1000)}"
        profile = find_profile(model, profile_name)
        if not profile:
            wall_thickness = 5  # default wall thickness
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
    # Assign the entity to the tree
    assign_container(model, sewer_entity)
    # Now we need to create the geometry. The process is as follows:
    # Calculate the length of the pipe section using the from and to manholes coordinates.
    # Calculate the direction vector of the pipe section using the from and to manholes coordinates.
    # Use the from manhole coordinates as the start point of the pipe section.
    # Extrude the given length.
    # Rotate the extrusion to the direction vector.

    # Calculate the length of the pipe section
    length = numpy.sqrt(
        (sewer.start.x - sewer.end.x) ** 2
        + (sewer.start.y - sewer.end.y) ** 2
        + (sewer.start.z - sewer.end.z) ** 2
    )
    # Calculate the direction vector
    direction = numpy.array(
        [
            sewer.end.x - sewer.start.x,
            sewer.end.y - sewer.start.y,
            sewer.end.z - sewer.start.z,
        ]
    )
    direction = direction / numpy.linalg.norm(direction)
    # Set the placement of the pipe section
    matrix = numpy.eye(4)
    matrix[:, 3][0:3] = (sewer.startx, sewer.start.y, sewer.start.z)
    representation = run(
        "geometry.add_profile_representation",
        model,
        context=context,
        profile=profile,
        depth=length,
    )
    # modify the matrix to the direction vector
    matrix[0:3, 0:3] = numpy.eye(3) - 2 * numpy.outer(direction, direction)
    # rotate the extrusion to the direction vector
    run(
        "geometry.edit_object_placement",
        model,
        product=sewer_entity,
        matrix=matrix,
    )
    run(
        "geometry.assign_representation",
        model,
        product=sewer_entity,
        representation=representation,
    )
