from datetime import date
from main_files.validators import validate_invoice
from main_files.convert import Invoice

def make_invoice(**overrides):
    """
    Tworzy poprawną fakturę bazową i pozwala nadpisać pola.
    Dzięki temu w testach zmieniasz tylko to, co potrzebne.
    """
    base = dict(
        source_file="fake.pdf",
        template="superstore_v1",
        invoice_number="39519",
        seller_name="SuperStore",
        bill_to="Aaron Bergman",
        ship_to=None,
        issue_date=date(2012, 2, 19),
        ship_mode="Standard Class",
        order_id="CA-2012-AB10015140-40958",
        subtotal=25.25,
        discount_amount=5.05,
        shipping=1.97,
        total=22.17,
        items=[],
    )
    base.update(overrides)
    return Invoice(**base)

def test_validate_invoice_ok_when_totals_match():
    inv = make_invoice()
    issues = validate_invoice(inv)
    assert issues == []


def test_validate_invoice_reports_missing_invoice_number():
    inv = make_invoice(invoice_number="")
    issues = validate_invoice(inv)
    assert "No invoice number." in issues


def test_validate_invoice_reports_missing_total():
    inv = make_invoice(total=None)
    issues = validate_invoice(inv)
    assert "NO_TOTAL" in issues


def test_validate_invoice_reports_total_mismatch_when_off_by_more_than_tolerance():
    # subtotal - discount + shipping = 25.25 - 5.05 + 1.97 = 22.17
    # Dajemy total mocno inne, żeby przekroczyć tolerancję 0.05
    inv = make_invoice(total=99.99)
    issues = validate_invoice(inv)
    assert "TOTAL_MISMATCH" in issues


def test_validate_invoice_does_not_report_total_mismatch_when_any_component_is_none():
    inv = make_invoice(subtotal=None)
    issues = validate_invoice(inv)
    assert "TOTAL_MISMATCH" not in issues
