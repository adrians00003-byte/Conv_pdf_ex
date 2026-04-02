from parser.superstore_v1 import SuperstoreV1Parser

PARSERS = [SuperstoreV1Parser()]

def select_parser(text: str):
    for p in PARSERS:
        if p.can_parse(text):
            return p
    return None
