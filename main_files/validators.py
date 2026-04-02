from main_files.convert import Invoice

def validate_invoice(inv: Invoice) -> list[str]:
    issues = []

    if not inv.invoice_number:
        issues.append("NO_INVOICE_NUMBER")

    if inv.total is None:
        issues.append("NO_TOTAL")

    if inv.subtotal is None:
        issues.append("NO_SUBTOTAL")

    if inv.shipping is None:
        issues.append("NO_SHIPPING")

    
    if inv.subtotal is not None and inv.shipping is not None and inv.total is not None:
        discount = inv.discount_amount if inv.discount_amount is not None else 0
        calculated_total = inv.subtotal - discount + inv.shipping

        diff = abs(calculated_total - inv.total)
        if diff > 0.05:
            issues.append("Toatl_mismatch")
    
    return issues