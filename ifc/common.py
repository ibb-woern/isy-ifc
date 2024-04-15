import math
import ifcopenshell
from ifcopenshell.api import run
from ifcopenshell.entity_instance import entity_instance
from typing import NamedTuple, Union

import numpy as np


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


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
            [0, 0, 0, 1],
        ]
    )


# Function to calculate rotation angles
def calculate_rotation_angles(point1: Point3D, point2: Point3D):
    # calculate direction vector
    point1 = np.array([point1.x, point1.y, point1.z])
    point2 = np.array([point2.x, point2.y, point2.z])
    dir_vector = point2 - point1

    # Normalize direction vector
    dir_vector /= np.linalg.norm(dir_vector)

    # Calculate rotation around X-axis
    theta_x = math.atan2(dir_vector[1], dir_vector[2])
    phi_x = math.atan2(
        math.sqrt(dir_vector[1] ** 2 + dir_vector[2] ** 2), dir_vector[0]
    )

    # Calculate rotation around Y-axis
    theta_y = math.atan2(dir_vector[0], dir_vector[2])
    phi_y = math.atan2(
        math.sqrt(dir_vector[0] ** 2 + dir_vector[2] ** 2), dir_vector[1]
    )

    # Calculate rotation around Z-axis
    theta_z = math.atan2(dir_vector[1], dir_vector[0])
    phi_z = math.atan2(
        math.sqrt(dir_vector[0] ** 2 + dir_vector[1] ** 2), dir_vector[2]
    )

    return (theta_x, phi_x), (theta_y, phi_y), (theta_z, phi_z)


# Function to construct the transformation matrix
def construct_transformation_matrix(rotations):
    # Initialize identity matrix
    transformation_matrix = np.eye(4)

    # Apply rotations around X, Y, and Z axes
    for axis, (theta, phi) in zip(["X", "Y", "Z"], rotations):
        axis_vector = np.zeros(3)
        axis_vector[ord(axis) - ord("X")] = 1
        rotation = rotation_matrix(axis_vector, theta)
        transformation_matrix = np.dot(transformation_matrix, rotation)
        rotation = rotation_matrix(axis_vector, phi)
        transformation_matrix = np.dot(transformation_matrix, rotation)

    return transformation_matrix
