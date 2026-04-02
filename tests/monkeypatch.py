from __future__ import annotations

from pathlib import Path

from main_files.pipeline import run_batch


# Minimalny tekst, który Twój parser Superstore powinien ogarnąć.
SUPERSTORE_TEXT_OK = (
    "INVOICE # 39519\n"
    "SUPERSTORE\n"
    "Bill To:\n"
    "Aaron Bergman\n"
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


def test_pipeline_happy_path_moves_to_archive_and_exports(monkeypatch, tmp_path: Path):
    # 1) Tworzymy foldery jak w realnym programie, ale w bezpiecznym tmp_path
    inbox_dir = tmp_path / "pdf"
    archive_dir = tmp_path / "archive"
    failed_dir = tmp_path / "failed"
    out_path = tmp_path / "out" / "invoices.xlsx"

    inbox_dir.mkdir(parents=True, exist_ok=True)

    # 2) Tworzymy 2 “udawane” pliki PDF (puste pliki z rozszerzeniem .pdf)
    (inbox_dir / "a.pdf").write_bytes(b"")
    (inbox_dir / "b.pdf").write_bytes(b"")

    # 3) Monkeypatch #1: zamiast czytać PDF-a, zawsze zwracaj nasz tekst
    def fake_extract_text(pdf_path: Path) -> str:
        return SUPERSTORE_TEXT_OK

    # UWAGA: patchujesz funkcję tam, gdzie jest UŻYWANA, czyli w module pipeline
    monkeypatch.setattr("main_files.pipeline.extract_text", fake_extract_text)

    # 4) Monkeypatch #2: zamiast pisać Excela, przechwyć dane do asercji
    captured = {}

    def fake_export_to_excel(invoices, errors, output_path):
        captured["invoices"] = invoices
        captured["errors"] = errors
        captured["output_path"] = str(output_path)
        return Path(output_path)

    monkeypatch.setattr("main_files.pipeline.export_to_excel", fake_export_to_excel)

    # 5) Odpalamy cały pipeline jak w produkcji
    run_batch(
        inbox_dir=inbox_dir,
        out_path=out_path,
        archive_dir=archive_dir,
        failed_dir=failed_dir,
    )

    # 6) Asercje: pipeline powinien przetworzyć 2 pliki => 2 faktury, 0 błędów
    assert "invoices" in captured
    assert len(captured["invoices"]) == 2
    assert captured["errors"] == []

    # 7) Asercje: pliki powinny zostać przeniesione do archive, inbox ma być pusty
    assert (archive_dir / "a.pdf").exists()
    assert (archive_dir / "b.pdf").exists()
    assert not (inbox_dir / "a.pdf").exists()
    assert not (inbox_dir / "b.pdf").exists()

    # 8) Asercje: failed powinien być pusty
    assert list(failed_dir.glob("*.pdf")) == []
