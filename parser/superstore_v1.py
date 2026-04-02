from __future__ import annotations

import re
from datetime import datetime

from parser.base import InvoiceParser
from main_files.convert import Invoice, InvoiceItem
from main_files.utils import money


def must(pattern: str, text: str, field: str, flags: int = 0) -> re.Match:
    """
    Szuka dopasowania regexem. Jeśli nie znajdzie – rzuca ValueError z nazwą pola.
    Dzięki temu w failed zobaczysz np. 'Missing field: bill_to', a nie 'NoneType...group'.
    """
    m = re.search(pattern, text, flags)
    if not m:
        raise ValueError(f"Missing field: {field} (pattern={pattern})")
    return m


class SuperstoreV1Parser(InvoiceParser):
    name = "superstore_v1"

    def can_parse(self, text: str) -> bool:
        t = text.upper()
        return ("INVOICE" in t) and ("SUPERSTORE" in t) and ("ORDER ID" in t)

    def parse(self, text: str, source_file: str) -> Invoice:
        # 1) Invoice number: w PDF jest "INVOICE\n# 39519"
        inv_no = must(r"INVOICE\s*#\s*(\d+)", text, "invoice_number").group(1)

        # 2) Bill To: w PDF jest:
        #    Bill To:
        #    Aaron Bergman
        # --- bill_to / ship_to / ship_mode block ---
        block_match = must(
            r"Bill To:\s*(.*?)\s*Balance Due:",
            text,
            "bill_ship_block",
            flags=re.DOTALL
        )

        block = block_match.group(1)

        lines = [line.strip() for line in block.splitlines() if line.strip()]

        # Oczekiwany układ po ekstrakcji bloków:
        # Ship To:
        # Ship Mode:
        # <ship_mode>
        # <bill_to>
        # <ship_to line 1>
        # <ship_to line 2>
        # ...

        if "Ship Mode:" not in lines:
            raise ValueError("Missing field: ship_mode label in bill/ship block")

        ship_mode_idx = lines.index("Ship Mode:")

        if len(lines) <= ship_mode_idx + 2:
            raise ValueError("Missing field: bill_to after ship_mode in bill/ship block")

        ship_mode = lines[ship_mode_idx + 1]
        bill_to = lines[ship_mode_idx + 2]
        ship_to = " ".join(lines[ship_mode_idx + 3:]) if len(lines) > ship_mode_idx + 3 else ""
        date_raw = must(
            r"Date:\s*([A-Za-z]{3}\s+\d{1,2}\s+\d{4})",
            text,
            "issue_date"
            ).group(1)

        # "Feb 19 2012" -> %b (skrót miesiąca), nie %B (pełna nazwa)
        issue_data = datetime.strptime(date_raw, "%b %d %Y").date()

        # 4) Order ID w PDF jest na dole:
        #    Order ID : CA-2012-AB10015140-40958
        order_id = must(r"Order ID\s*:\s*(.+)", text, "order_id").group(1).strip()
        # znajdź fragment tekstu od "Subtotal:" do końca
        start = text.upper().rfind("SUBTOTAL:")
        if start == -1:
            raise ValueError("Missing field: subtotal block start (Subtotal:)")
        
        totals_text = text[start:]
        amount_lines = re.findall(r"^\$([\d,]+\.\d{2})\s*$", totals_text, flags=re.MULTILINE)

        if len(amount_lines) == 4:
            subtotal_s, discount_s, shipping_s, total_s = amount_lines
            discount = money(discount_s)
        elif len(amount_lines) == 3:
            subtotal_s, shipping_s, total_s = amount_lines
            discount = 0.0
        else:
            raise ValueError(f"Unexpected totals block: expected 3 or 4 money lines, got {len(amount_lines)}")

        subtotal = money(subtotal_s)
        shipping = money(shipping_s)
        total = money(total_s)

        # 6) Pozycje: w tym PDF jest linia np.
        #    Akro Stacking Bins 2 $12.62 $25.25
        items: list[InvoiceItem] = []
        m = re.search(r"(.+?)\s+(\d+)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})", text)
        if m:
            items.append(
                InvoiceItem(
                    description=m.group(1).strip(),
                    quantity=float(m.group(2)),
                    rate=money(m.group(3)),
                    amount=money(m.group(4)),
                )
            )

        return Invoice(
            source_file=source_file,
            template=self.name,
            invoice_number=inv_no,
            seller_name="SuperStore",
            bill_to=bill_to,
            ship_to=ship_to,
            issue_data=issue_data,
            ship_mode=ship_mode,
            order_id=order_id,
            subtotal=subtotal,
            discount_amount=discount,
            shipping=shipping,
            total=total,
            items=items,
        )
