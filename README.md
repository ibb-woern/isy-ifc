# Disclaimer

**WARNING: THIS IS AN EXPERIMENTAL PROJECT**

# Scope

The aim of this project is to accomplish the following tasks:

- Extract information from an ISYBAU-XML file.
- Utilize [IfcOpenShell](https://ifcopenshell.org/) to generate geometry based on the extracted data, initially focusing on precast/standardized elements.
- Map the data to the [IFC-Schema 4x3](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/).

# ISYBAU

The German [ISYBAU](https://www.bfr-abwasser.de/html/A7ISYBAU_ATF_XML.html) wastewater exchange formats facilitate standardized, XML-based data exchange of sewer data between clients (e.g., State Building Management), contractors (e.g., engineering offices), or other project participants (e.g., surveying engineering offices or inspection companies).

The standard is well-documented, and [real-world examples](https://www.bfr-abwasser.de/html/Materialien.1.40.html) are available, which will serve as references during implementation.

# Terms and Definitions

![Terms and Conditions Schema](docs/term_definitions.svg)
