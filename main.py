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
    project = run("root.create_entity", model,
                  ifc_class="IfcProject", name="Isy IFC")

    site = run("root.create_entity", model,
               ifc_class="IfcSite", name="Isy IFC site")
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
    # Your main code goes here
    start_manhole = Manhole(0.0, 0.0, 450.0, 455.0)
    end_manhole = Manhole(35.0, 35.0, 449.0, 454.0)
    pipe_section = PipeSection(start_manhole, end_manhole, diameter_inner=0.3)

    # start ifc creation
    model, body = _setup_ifc()

    profile_circle = model.create_entity("IfcCircleProfileDef", ProfileName="DN1000", ProfileType="AREA",
                                         Radius=1)
    manhole_entity = run("root.create_entity", model,
                         ifc_class="IfcDistributionChamberElement", name="Manhole 1",)
    # change object placement to matrix (5,3,1)
    matrix = numpy.eye(4)
    matrix[:, 3][0:3] = (2, 3, 5)
    run("geometry.edit_object_placement", model,
        product=manhole_entity, matrix=matrix, is_si=True)
    # create representation. Extrude the circle profile by the height of 5 meters
    representation = run("geometry.add_profile_representation",
                         model, context=body, profile=profile_circle, depth=5)
    run("geometry.assign_representation", model, product=manhole_entity,
        representation=representation)

    model.write(Path.cwd().joinpath("output") / "test.ifc")


if __name__ == "__main__":
    main()
