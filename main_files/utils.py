from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


def money(value: Any) -> float:
    """
    Zamienia kwotę wyciągniętą z PDF (np. "1,234.56", "$1,234.56", 1234.56)
    na liczbę float.

    Dlaczego float, a nie Decimal?
    - Na MVP Ci wystarczy float do walidacji i Excela.
    - Jeśli będziesz chciał „księgowo poprawnie”, później przejdziemy na Decimal end-to-end.
    """
    if value is None:
        return 0.0

    # 1) Zamieniamy input na string, bo z regexów dostajesz zwykle tekst
    s = str(value).strip()

    # 2) Usuwamy symbol waluty i spacje (często w PDF jest "$ 1,234.56")
    s = s.replace("$", "").replace(" ", "")

    # 3) Usuwamy separatory tysięcy ("," w formacie USA)
    s = s.replace(",", "")

    # 4) Zamieniamy na Decimal (bezpieczniej niż float na etapie parsowania)
    try:
        dec = Decimal(s)
    except (InvalidOperation, ValueError):
        # Jeśli tekst jest „śmieciowy” (np. pusty albo coś nie-liczbowego),
        # zwracamy 0.0 żeby nie wywalić całego batcha.
        return 0.0

    # 5) Konwersja do float na potrzeby Twoich modeli/Excela
    return float(dec)
