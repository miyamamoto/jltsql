"""Table name mapping: jltsql -> JRA-VAN Standard."""

from typing import Dict


# Mapping from JRA-VAN standard table names to jltsql table names
JRAVAN_TO_JLTSQL: Dict[str, str] = {
    "BANUSI": "NL_HN",
    "CHOKYO": "NL_CH",
    "HANSYOKU": "NL_BR",
    "HARAI": "NL_HR",
    "KISYU": "NL_KS",
    "ODDS_SANREN": "NL_O5",
    "ODDS_SANRENTAN": "NL_O6",
    "ODDS_TANPUKU": "NL_H1",
    "ODDS_UMAREN": "NL_O1",
    "ODDS_UMATAN": "NL_O4",
    "ODDS_WAKU": "NL_O3",
    "ODDS_WIDE": "NL_O2",
    "RACE": "NL_RA",
    "SCHEDULE": "NL_YS",
    "SEISAN": "NL_BN",
    "TOKU": "NL_TK",
    "TOKU_RACE": "NL_TK",
    "UMA": "NL_UM",
    "UMA_RACE": "NL_SE",
}

# Reverse mapping
JLTSQL_TO_JRAVAN: Dict[str, str] = {
    v: k for k, v in JRAVAN_TO_JLTSQL.items()
}
