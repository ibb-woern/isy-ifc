import numpy
from models.manhole import Manhole
from models.types import ManholeFormType
from ifcopenshell.api import run
from ifcopenshell.entity_instance import entity_instance
from typing import Union


def _find_profile(model, profile_name) -> Union[None, entity_instance]:
    profiles = model.by_type("IfcProfileDef")
    for profile in profiles:
        # ProfileName is the second attribute. Somehow profile.Name does not work.
        if profile[1] == profile_name:
            return profile
    return None


def _assign_container(model, entity):
    # TODO: Proper assignments. Currently only one is supported.
    container = model.by_type("IfcFacility")[0]
    if not container:
        container = model.by_type("IfcBuilding")[0]

    if not container:
        raise ValueError("No container found to assign the entity to")
    run(
        "spatial.assign_container",
        model,
        relating_structure=container,
        products=[entity],
    )


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
        profile = _find_profile(model, profile_name)
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
        profile = _find_profile(model, profile_name)
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
