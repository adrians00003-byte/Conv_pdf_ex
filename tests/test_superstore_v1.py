import pytest

from parser.superstore_v1 import SuperstoreV1Parser


# --------- Dane testowe (surowy tekst jak po extract_text) ---------
SUPERSTORE_TEXT_OK = (
    "INVOICE # 39519\n"
    "SUPERSTORE\n"
    "Bill To: \nAaron Bergman\n"
    "Date: Feb 19 2012\n"
    "Ship Mode: Standard Class\n"
    "Order ID : CA-2012-AB10015140-40958\n"
    "\n"
    "Quantity\n"
    "Rate\n"
    "Amount\n"
    "Akro Stacking Bins\n"
    "2\n"
    "$12.62\n"
    "$25.25\n"
    "Storage, Office Supplies, OFF-ST-3078\n"
    "\n"
    "Subtotal:\n"
    "$25.25\n"
    "Discount (20%):\n"
    "$5.05\n"
    "Shipping:\n"
    "$1.97\n"
    "Total:\n"
    "$22.17\n"
    "\n"
    "Notes:\n"
    "Thanks for your business!\n"
)


SUPERSTORE_TEXT_NO_MATCH = (
    "FAKTURA VAT\n"
    "Sprzedawca: Januszex Sp. z o.o.\n"
    "Razem: 123,00 PLN\n"
)


# --------- Testy ---------
def test_can_parse_true_for_superstore_text():
    parser = SuperstoreV1Parser()
    assert parser.can_parse(SUPERSTORE_TEXT_OK) is True


def test_can_parse_false_for_other_documents():
    parser = SuperstoreV1Parser()
    assert parser.can_parse(SUPERSTORE_TEXT_NO_MATCH) is False


def test_parse_happy_path_extracts_fields_correctly():
    parser = SuperstoreV1Parser()

    invoice = parser.parse(text=SUPERSTORE_TEXT_OK, source_file="fake.pdf")

    # nagłówek
    assert invoice.source_file == "fake.pdf"
    assert invoice.template == parser.name
    assert invoice.invoice_number == "39519"
    assert invoice.seller_name == "SuperStore"
    assert invoice.bill_to == "Aaron Bergman"

    # daty/identyfikatory (zależnie jak masz w modelu)
    assert str(invoice.issue_data) == "2012-02-19"
    assert invoice.ship_mode == "Standard Class"
    assert invoice.order_id == "CA-2012-AB10015140-40958"

    # kwoty
    assert invoice.subtotal == 25.25
    assert invoice.discount_amount == 5.05
    assert invoice.shipping == 1.97
    assert invoice.total == 22.17

    # pozycje
    assert len(invoice.items) >= 1
    first = invoice.items[0]
    assert first.description == "Akro Stacking Bins"
    assert first.quantity == 2.0
    assert first.rate == 12.62
    assert first.amount == 25.25


def test_parse_missing_subtotal_should_fail_cleanly():
    parser = SuperstoreV1Parser()

    bad_text = SUPERSTORE_TEXT_OK.replace("Subtotal:\n$25.25\n", "Subtotal:\n\n")

    # Jeśli masz helper typu must(...), to powinno być ValueError.
    # Jeżeli nadal używasz re.search(...).group(1) bez zabezpieczenia,
    # to poleci AttributeError ('NoneType'...).
    with pytest.raises((ValueError, AttributeError)):
        parser.parse(text=bad_text, source_file="fake.pdf")
