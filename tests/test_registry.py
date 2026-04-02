from parser.registry import select_parser
from parser.superstore_v1 import SuperstoreV1Parser

SUPERSTORE_TEXT = (
    "INVOICE # 39612\n"
    "SUPERSTORE\n"
    "Order ID : CA-2012-AB100151140-40958\n"
)

OTHER_TEXT = (
    "FASKTURA VAT\n"
    "Sprzedawca: Januszex\n"
)

def test_select_parser():
    p = select_parser(SUPERSTORE_TEXT)

    assert p is not None
    assert isinstance(p, SuperstoreV1Parser)
    assert p.name == "superstore_v1"

def test_select_parser_return_none_when_no_parser_matches():
    p = select_parser(OTHER_TEXT)

    assert p is None
