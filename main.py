import click
import parser.isybau as isybau
import parser.bbsoft_xlsx as bbsoft
from pathlib import Path


@click.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
def main(input_file: Path):
    # Check if the file is an XML file. if so call the isybau parser
    if input_file.suffix == ".xml":
        isybau.parse(input_file)
        return
    if input_file.suffix == ".xlsx":
        bbsoft.parse(input_file)
        return
    print("Unsupported file format")
    return


if __name__ == "__main__":
    main()
