import click
import parser.isybau as isybau
import parser.bbsoft_ods as bbsoft
from pathlib import Path


@click.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
def main(input_file: Path):
    # Check if the file is an XML file. if so call the isybau parser
    if input_file.suffix == ".xml":
        isybau.parse(input_file)
    if input_file.suffix == ".ods":
        bbsoft.parse(input_file)


if __name__ == "__main__":
    main()
