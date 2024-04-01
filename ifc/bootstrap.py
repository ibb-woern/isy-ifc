import ifcopenshell
from ifcopenshell.api import run as _run


def setup() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    model = ifcopenshell.file(schema="IFC4x3")

    # Create the IFC hierarchy
    # PROJECT CREATION NEEDS TO BE DONE FIRST
    project = _run("root.create_entity", model, ifc_class="IfcProject", name="Isy IFC")

    site = _run("root.create_entity", model, ifc_class="IfcSite", name="Isy IFC site")
    _run("aggregate.assign_object", model, relating_object=project, product=site)

    facility = _run(
        "root.create_entity", model, ifc_class="IfcFacility", name="Isy IFC facility"
    )
    _run("aggregate.assign_object", model, relating_object=site, product=facility)

    # Setup the context for the model
    model3d = _run("context.add_context", model, context_type="Model")
    body = _run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model3d,
    )

    # Setup units
    length = _run("unit.add_si_unit", model, unit_type="LENGTHUNIT")  # meters
    _run("unit.assign_unit", model, units=[length])

    return model, body
