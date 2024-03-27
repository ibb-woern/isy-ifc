from math import sqrt
from pathlib import Path
import ifcopenshell
from ifcopenshell.api import run
from models.manhole import Manhole
from models.pipe_section import PipeSection

import numpy


def _setup_ifc() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
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

    return model, body


def main():
    manholes = [
        Manhole("Start", 0.0, 0.0, 450.0, 455.0),
        Manhole("End", 35.0, 35.0, 449.0, 454.0),
    ]

    pipe_sections = [
        PipeSection(manholes[0].name, manholes[0], manholes[1], 300, 320),
    ]

    # start ifc creation
    model, body = _setup_ifc()

    profile_circle = model.create_entity(
        "IfcCircleProfileDef", ProfileName="DN1000", ProfileType="AREA", Radius=1
    )
    for ml in manholes:
        manhole_entity = run(
            "root.create_entity",
            model,
            ifc_class="IfcDistributionChamberElement",
            name=ml.name,
        )
        matrix = numpy.eye(4)
        matrix[:, 3][0:3] = (ml.x, ml.y, ml.z)
        run(
            "geometry.edit_object_placement",
            model,
            product=manhole_entity,
            matrix=matrix,
            is_si=True,
        )
        representation = run(
            "geometry.add_profile_representation",
            model,
            context=body,
            profile=profile_circle,
            depth=ml.z_top - ml.z,
        )
        run(
            "geometry.assign_representation",
            model,
            product=manhole_entity,
            representation=representation,
        )

    profile_dn300sb = model.create_entity(
        "IfcCircleHollowProfileDef",
        ProfileName="300SB",
        ProfileType="AREA",
        Radius=0.15,
        WallThickness=0.1,
    )

    for ps in pipe_sections:
        pipe_section_entity = run(
            "root.create_entity", model, ifc_class="IfcPipeSegment", name=ps.name
        )
        matrix = numpy.eye(4)
        matrix[:, 3][0:3] = (ps.start.x, ps.start.y, ps.start.z)
        extrusion_vector = (
            ps.end.x - ps.start.x,
            ps.end.y - ps.start.y,
            ps.end.z - ps.start.z,
        )
        # length
        extrusion_length = sqrt(
            extrusion_vector[0] ** 2
            + extrusion_vector[1] ** 2
            + extrusion_vector[2] ** 2
        )
        # apply extrusion vector
        matrix[0:3, 2] = extrusion_vector

        run(
            "geometry.edit_object_placement",
            model,
            product=pipe_section_entity,
            matrix=matrix,
            is_si=True,
        )
        representation = run(
            "geometry.add_profile_representation",
            model,
            context=body,
            profile=profile_dn300sb,
            depth=extrusion_length,
        )
        run(
            "geometry.assign_representation",
            model,
            product=pipe_section_entity,
            representation=representation,
        )

    model.write(Path.cwd().joinpath("output") / "test.ifc")


if __name__ == "__main__":
    main()
