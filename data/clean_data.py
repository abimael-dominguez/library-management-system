from __future__ import annotations

import argparse
import csv
import datetime as dt
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data/raw/library-cbg.tsv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/library-cbg-clean.csv"

COLUMN_MAPPING = {
    "nombre": "title",
    "autor": "author",
    "pz": "total_copies",
    "paginas": "pages",
    "semanas_aut": "max_loan_weeks",
    "estatus": "status",
    "encargado": "employee",
    "congregante": "member",
    "fecha_de_prestamo": "loan_date",
    "fecha_estimada_de_entrega": "due_date",
    "fecha_r_de_entrega": "actual_return_date",
}

TEXT_COLUMNS = {"title", "author", "status", "employee", "member"}
DATE_COLUMNS = {"loan_date", "due_date", "actual_return_date"}
PLACEHOLDER_VALUES = {"-"}


def to_ascii_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_value = "".join(character for character in normalized if not unicodedata.combining(character))
    return ascii_value.replace(".", "").replace(" ", "_")


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_display_text(value: str) -> str:
    cleaned = normalize_text(value)
    if cleaned in PLACEHOLDER_VALUES:
        return ""
    if cleaned.isupper():
        return cleaned.title()
    return cleaned


def normalize_date(value: str) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return cleaned


def clean_row(row: list[str], headers: list[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for header, cell in zip(headers, row, strict=False):
        if header in DATE_COLUMNS:
            output[header] = normalize_date(cell)
        elif header in TEXT_COLUMNS:
            output[header] = normalize_display_text(cell)
        else:
            output[header] = normalize_text(cell)
    return output


def clean_data(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> None:
    with input_path.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.reader(infile, delimiter="\t")
        raw_headers = next(reader)
        headers = [COLUMN_MAPPING.get(to_ascii_key(cell), to_ascii_key(cell)) for cell in raw_headers]
        rows = [clean_row(row, headers) for row in reader]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean the raw library TSV export into import-ready CSV.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    clean_data(args.input, args.output)
