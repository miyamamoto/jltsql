"""Parser for AV record - Generated from reference schema.

This parser uses correct field positions calculated from schema field lengths.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class AVParser(BaseParser):
    """Parser for AV record with accurate field positions.

    Total record length: 140 bytes
    Fields: 7
    """

    record_type = "AV"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions calculated from schema.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            # JV-Data standard header fields
            FieldDef("RecordSpec", 0, 2),      # Record type ID (positions 1-2)
            FieldDef("DataKubun", 2, 1),       # Data type (position 3)
            # Data fields
            FieldDef("KettoNum", 3, 10),       # Horse registration number
            FieldDef("SaleHostName", 13, 40),  # Sale host name
            FieldDef("SaleName", 53, 80),      # Sale name
            FieldDef("Price", 133, 10),        # Price
            # Record delimiter at the end (last 2 bytes)
            FieldDef("RecordDelimiter", 138, 2),  # Record delimiter (CRLF)
        ]
