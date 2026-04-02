from __future__ import annotations

from pathlib import Path
import shutil

from extract.pdf_text import extract_text
from parser.registry import select_parser
from main_files.validators import validate_invoice
from excel.import_2_excel import export_to_excel

def run_batch(
    inbox_dir: str | Path = "pdf",
    out_path: str | Path = "out/invoices.xlsx",
    archive_dir: str | Path = "archive",
    failed_dir: str | Path = "failed",
) -> None:
    inbox_dir = Path(inbox_dir)
    archive_dir = Path(archive_dir)
    failed_dir = Path(failed_dir)

    archive_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    invoices = []
    errors = []

    pdf_files = sorted(inbox_dir.glob("*.pdf"))
    for pdf_path in pdf_files:
        try:
            text = extract_text(pdf_path)
            # --- DIAGNOSTYKA: pokaż jak wygląda okolica "Subtotal" w surowym tekście ---
            #i = text.upper().find("SUBTOTAL")
            #print("\n=== DEBUG: okolica SUBTOTAL ===")
            #print(repr(text[max(0, i-120): i+200]))
            #print("=== /DEBUG ===\n")

            parser = select_parser(text)
            if not parser:
                errors.append({
                    "source_file": str(pdf_path),
                    "error_type": "NO_PARSER",
                    "error_message": "Nie znaleziono parsera pasującego do dokumentu",
                    "template": "unknown",
                })
                shutil.move(str(pdf_path), failed_dir / pdf_path.name)
                continue

            invoice = parser.parse(text=text, source_file=str(pdf_path))

            issues = validate_invoice(invoice)
            if issues:
                errors.append({
                    "source_file": str(pdf_path),
                    "error_type": "VALIDATION_FAIL",
                    "error_message": ";".join(issues),
                    "template": getattr(parser, "name", "unknown"),
                })
                shutil.move(str(pdf_path), failed_dir / pdf_path.name)
            else:
                shutil.move(str(pdf_path), archive_dir / pdf_path.name)

            invoices.append(invoice)
            

        except Exception as e:
            errors.append({
                "source_file": str(pdf_path),
                "error_type": "EXCEPTION",
                "error_message": str(e),
                "template": "unknown",
            })
            # jak się wywaliło, też do failed
            try:
                shutil.move(str(pdf_path), failed_dir / pdf_path.name)
            except Exception:
                pass
    
    export_to_excel(invoices=invoices, errors=errors, output_path=out_path)
