from __future__ import annotations

import argparse
from pathlib import Path

from main_files.pipeline import run_batch


def main() -> None:
    # 1. Tworzymy parser argumentów CLI
    parser = argparse.ArgumentParser(
        description="PDF → Excel invoice processing pipeline"
    )

    # 2. Dodajemy argumenty (czyli opcje z terminala)
    parser.add_argument(
        "--inbox",
        type=Path,
        default=Path("pdf"),
        help="Folder z PDF-ami do przetworzenia (domyślnie: ./pdf)",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("out/invoices.xlsx"),
        help="Plik wynikowy Excel (domyślnie: out/invoices.xlsx)",
    )

    parser.add_argument(
        "--archive",
        type=Path,
        default=Path("archive"),
        help="Folder na poprawnie przetworzone pliki",
    )

    parser.add_argument(
        "--failed",
        type=Path,
        default=Path("failed"),
        help="Folder na błędne pliki",
    )

    # 3. Parsujemy argumenty z terminala
    args = parser.parse_args()

    # 4. Wywołujemy Twój pipeline
    run_batch(
        inbox_dir=args.inbox,
        out_path=args.out,
        archive_dir=args.archive,
        failed_dir=args.failed,
    )


if __name__ == "__main__":
    main()
