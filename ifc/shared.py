import ifcopenshell
from ifcopenshell.api import run
from ifcopenshell.entity_instance import entity_instance
from typing import List, NamedTuple, Union

import numpy as np

from models.manhole import Manhole


class Point3D(NamedTuple):
    x: float
    y: float
    z: float


def setup() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    model = ifcopenshell.file(schema="IFC4x3")

    # Create the IFC hierarchy
    # PROJECT CREATION NEEDS TO BE DONE FIRST
    project = run("root.create_entity", model, ifc_class="IfcProject", name="Isy IFC")

    site = run("root.create_entity", model, ifc_class="IfcSite", name="Isy IFC site")
    run("aggregate.assign_object", model, relating_object=project, product=site)

    facility = run(
        "root.create_entity", model, ifc_class="IfcFacility", name="Isy IFC facility"
    )
    run("aggregate.assign_object", model, relating_object=site, product=facility)

    # Setup the context for the model
    model3d = run("context.add_context", model, context_type="Model")
    body = run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model3d,
    )

    # Setup units
    length = run("unit.add_si_unit", model, unit_type="LENGTHUNIT")  # meters
    run("unit.assign_unit", model, units=[length])

    # TODO: Implement proper georeferencing while respecting user input
    run("georeference.add_georeferencing", model)
    run("georeference.edit_georeferencing", model, projected_crs={"Name": "EPSG:25832"})

    return model, body


def find_profile(model, profile_name) -> Union[None, entity_instance]:
    profiles = model.by_type("IfcProfileDef")
    for profile in profiles:
        # ProfileName is the second attribute. Somehow profile.Name does not work.
        if profile[1] == profile_name:
            return profile
    return None


def assign_container(model, entity):
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


def extrusion_rotation_angles(point1: Point3D, point2: Point3D) -> tuple[float, float]:
    # Calculate the vector from point1 to point2
    vector = np.array(point2) - np.array(point1)
    # Calculate the angle between the vector and the Z axis
    angle_y = np.arctan2(vector[0], vector[2])
    angle_x = np.arctan2(-vector[1], np.sqrt(vector[0] ** 2 + vector[2] ** 2))
    # Convert angles from radians to degrees
    angle_x = np.degrees(angle_x)
    angle_y = np.degrees(angle_y)
    return angle_x, angle_y


def find_manhole_by_name(name: str, manholes: List[Manhole]) -> Union[Manhole, None]:
    for manhole in manholes:
        if str(manhole.name) == str(name):
            return manhole
    return None
