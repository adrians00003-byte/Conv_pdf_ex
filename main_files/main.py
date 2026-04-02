from __future__ import annotations

import argparse
from pathlib import Path
from .pipeline import run_batch


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Budujemy parser argumentów CLI.
    Ten obiekt opisuje: jakie parametry przyjmuje program i jak je czytać z terminala.
    """
    p = argparse.ArgumentParser(
        prog="conv_pdf_ex",
        description="Batch: PDF faktury -> parsowanie -> walidacja -> Excel (ETL)",
    )

    p.add_argument(
        "--inbox",
        default="pdf",
        help="Folder z PDF-ami wejściowymi (domyślnie: pdf)",
    )
    p.add_argument(
        "--out",
        default="out/invoices.xlsx",
        help="Ścieżka pliku wynikowego .xlsx (domyślnie: out/invoices.xlsx)",
    )
    p.add_argument(
        "--archive",
        default="archive",
        help="Folder dla poprawnie przetworzonych PDF (domyślnie: archive)",
    )
    p.add_argument(
        "--failed",
        default="failed",
        help="Folder dla PDF z błędami (domyślnie: failed)",
    )

    return p


def main() -> int:
    """
    Główna funkcja programu:
    - czyta argumenty z terminala,
    - normalizuje ścieżki,
    - wywołuje pipeline.run_batch(...)
    """
    parser = build_arg_parser()
    args = parser.parse_args()

    inbox_dir = Path(args.inbox)
    out_path = Path(args.out)
    archive_dir = Path(args.archive)
    failed_dir = Path(args.failed)

    run_batch(
        inbox_dir=inbox_dir,
        out_path=out_path,
        archive_dir=archive_dir,
        failed_dir=failed_dir,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
