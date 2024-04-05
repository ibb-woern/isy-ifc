import numpy
from models.manhole import Manhole
from models.types import ManholeFormType
from ifcopenshell.api import run


def _profile_exists(model, profile_name):
    # Todo: Implement a proper check if the profile already exists
    return False


def _assign_container(model, entity):
    # TODO: Proper assignments. Currently only one is supported.
    container = model.by_type("IfcFacility")[0]
    if not container:
        container = model.by_type("IfcBuilding")[0]

    if not container:
        raise ValueError("No container found to assign the entity to")

    run("spatial.assign_container", model, relating_structure=container, product=entity)


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
        profile_name = f"{manhole.nominal_length}x{manhole.nominal_width}"
        if not _profile_exists(model, profile_name):
            if not manhole.nominal_width:
                manhole.nominal_width = manhole.nominal_length  # assume its a square
            profile = model.create_entity(
                "IfcRectangleProfileDef",
                ProfileName=f"{manhole.nominal_length}x{manhole.nominal_width}",
                ProfileType="AREA",
                XDim=manhole.nominal_length,
                YDim=manhole.nominal_width,
            )
    if manhole.form == ManholeFormType.CIRCULAR:
        profile_name = f"DN{manhole.nominal_length}"
        if not _profile_exists(model, profile_name):
            profile = model.create_entity(
                "IfcCircleProfileDef",
                ProfileName=f"{manhole.nominal_length}",
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
    _assign_container(model, manhole_entity)

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
        depth=manhole.z_top - manhole.z,
    )
    run(
        "geometry.assign_representation",
        model,
        product=manhole_entity,
        representation=representation,
    )
