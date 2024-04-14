import click
import parser.isybau as isybau
import parser.bbsoft_xlsx as bbsoft
import ifc.common as bootstrap
import ifc.entity_creator as entity_creator
from pathlib import Path


@click.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
@click.option("--output-file", type=click.Path(path_type=Path), default=None)
def main(input_file: Path, output_file: Path = None):
    # Check if the file is an XML file. if so call the isybau parser
    if input_file.suffix == ".xml":
        isybau.parse(input_file)
        return

    if input_file.suffix == ".xlsx":
        manholes, sewers = bbsoft.parse(input_file)
        model, body = bootstrap.setup()
        for manhole in manholes:
            entity_creator.manhole(manhole, model, body)
        for sewer in sewers:
            entity_creator.sewer(sewer, model, body)
        out_path = (
            output_file
            or Path.cwd().joinpath("output") / input_file.with_suffix(".ifc").name
        )
        model.write(out_path)
        return

    print("Unsupported file format")
    return


if __name__ == "__main__":
    main()
