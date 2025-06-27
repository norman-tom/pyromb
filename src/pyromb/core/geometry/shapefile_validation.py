from matplotlib.ft2font import SFNT
from shapely.geometry import shape
from shapely.validation import explain_validity
import shapefile as sf
import logging


def validate_shapefile_geometries(shp: sf.Reader, shapefile_name: str) -> bool:
    """
    Validate the geometries of a shapefile.

    Parameters
    ----------
    shp : shapefile.Reader
        The shapefile reader object.
    shapefile_name : str
        The name of the shapefile (for logging purposes).

    Returns
    -------
    bool
        True if all geometries are valid, False otherwise.
    """
    validation_passed = True
    for idx, shp_rec in enumerate(shp.shapes()):
        geom = shape(shp_rec.__geo_interface__)
        if not geom.is_valid:
            validity_reason = explain_validity(geom)
            logging.error(
                f"Invalid geometry in {shapefile_name} at Shape ID {idx}: {validity_reason}"
            )
            validation_passed = False

    if validation_passed:
        logging.info(f"All geometries in {shapefile_name} are valid.")

    return validation_passed


import logging
import shapefile as sf
from typing import List, Tuple


def validate_shapefile_fields(
    shp: sf.Reader, shapefile_name: str, expected_fields: List[Tuple[str, str]]
) -> bool:
    """
    Validate the fields of a shapefile against expected field names and types.
    Additionally, ensure that required fields contain valid data (not None or empty).

    Args:
        shp (sf.Reader): Shapefile reader object.
        shapefile_name (str): Name of the shapefile for logging purposes.
        expected_fields (List[Tuple[str, str]]): List of tuples containing expected field names and their types.

    Returns:
        bool: True if all expected fields are present with correct types and contain valid data, False otherwise.
    """
    TYPE_MAPPING = {
        "C": "Character",
        "N": "Numeric",
        "F": "Float",
        "L": "Logical",
        "D": "Date",
        "G": "General",
        "M": "Memo",
    }

    actual_fields = shp.fields[1:]  # Skip DeletionFlag field
    actual_field_names = [field[0] for field in actual_fields]
    actual_field_types = [field[1] for field in actual_fields]

    logging.info(f"\nValidating fields for {shapefile_name}:")
    for name, type_code in zip(actual_field_names, actual_field_types):
        type_desc = TYPE_MAPPING.get(type_code, "Unknown")
        logging.info(f"  Field Name: {name}, Type: {type_code} ({type_desc})")

    validation_passed = True

    # Field Name and Type Validation
    for exp_field, exp_type in expected_fields:
        if exp_field not in actual_field_names:
            logging.error(f"Missing expected field '{exp_field}' in {shapefile_name}.")
            validation_passed = False
        else:
            idx = actual_field_names.index(exp_field)
            act_type = actual_field_types[idx]
            if act_type != exp_type:
                type_desc = TYPE_MAPPING.get(act_type, "Unknown")
                logging.error(
                    f"Type mismatch for field '{exp_field}' in {shapefile_name}: "
                    f"Expected '{exp_type}' ({TYPE_MAPPING.get(exp_type, 'Unknown')}), "
                    f"Got '{act_type}' ({type_desc})"
                )
                validation_passed = False

    # Data Validation: Check for None or Empty Values in Required Fields
    if validation_passed:
        logging.info(f"Validating data integrity for fields in {shapefile_name}...")
        for record_num, record in enumerate(shp.records(), start=1):
            for exp_field, _ in expected_fields:
                value = record[exp_field]
                if value is None or (isinstance(value, str) and not value.strip()):
                    logging.error(
                        f"Empty or None value found in field '{exp_field}' "
                        f"for record {record_num} in {shapefile_name}."
                    )
                    validation_passed = False
        if validation_passed:
            logging.info(f"All required fields contain valid data in {shapefile_name}.")

    return validation_passed


def validate_confluences_out_field(shp: sf.Reader, shapefile_name: str) -> bool:
    """
    Validate that the 'out' field in the Confluences shapefile has exactly one '1' and the rest '0'.

    Args:
        shp (sf.Reader): Shapefile reader object.
        shapefile_name (str): Name of the shapefile for logging purposes.

    Returns:
        bool: True if the validation passes, False otherwise.
    """
    out_values = [record["out"] for record in shp.records()]

    count_ones = out_values.count(1)
    count_zeros = out_values.count(0)
    total_records = len(out_values)

    if count_ones != 1:
        logging.error(
            f"The 'out' field in {shapefile_name} should have exactly one '1'. Found {count_ones}."
        )
        return False

    if count_zeros != (total_records - 1):
        logging.error(
            f"The 'out' field in {shapefile_name} should have {total_records - 1} '0's. Found {count_zeros}."
        )
        return False

    logging.info(
        f"'out' field validation passed for {shapefile_name}: 1 '1' and {count_zeros} '0's."
    )
    return True
