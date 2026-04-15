from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pdfplumber


CONTRACT_PATTERN = re.compile(r"\bCO-\d{2,4}-\d{4}\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
PLATE_PATTERN = re.compile(r"\b[A-Z]{3}\d{3}\b")
REMI_NUMBER_PATTERN = re.compile(r"(?:REMI(?:SI[ÓO]N)?\D*)(\d{2,8})", re.IGNORECASE)
QTY_PATTERN = re.compile(r"\b(?:CANTIDAD|QTY|CANT)\D{0,8}(\d{1,4})\b", re.IGNORECASE)


def normalize_date(value: str) -> str:
    match = DATE_PATTERN.search(value)
    if not match:
        return "11/03/2026"
    day, month, year = match.groups()
    return f"{int(day):02d}/{int(month):02d}/{year}"


def extract_text_from_pdf(path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            parts.append(text)
    return "\n".join(parts)


def infer_remision_number(filename: str, full_text: str) -> str:
    by_name = REMI_NUMBER_PATTERN.search(filename)
    if by_name:
        return by_name.group(1)

    by_text = REMI_NUMBER_PATTERN.search(full_text)
    if by_text:
        return by_text.group(1)

    fallback = re.search(r"(\d{2,8})", filename)
    if fallback:
        return fallback.group(1)

    raise ValueError(
        "No fue posible inferir el número de remisión. Usa un nombre tipo REMISION_0106.pdf"
    )


def parse_remision(remision_path: str) -> dict[str, Any]:
    path = Path(remision_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de Remisión: {path}")

    text = extract_text_from_pdf(path)

    contract_match = CONTRACT_PATTERN.search(text)
    date_match = DATE_PATTERN.search(text)
    plate_match = PLATE_PATTERN.search(text)
    qty_match = QTY_PATTERN.search(text)

    remi_number = infer_remision_number(path.name, text)
    contract_number = contract_match.group(0).upper() if contract_match else "CO-235-2026"
    contract_date = normalize_date(date_match.group(0)) if date_match else "11/03/2026"
    plate = plate_match.group(0).upper() if plate_match else "UEV510"
    qty = qty_match.group(1) if qty_match else "15"

    return {
        "descripcion_item": "TERRAPLEN",
        "cantidad": qty,
        "serial": "",
        "contrato": contract_number,
        "fecha_contrato": contract_date,
        "propietario": "SONEP",
        "observaciones": f"TERRAPLEN - {qty}",
        "placa": plate,
        "tipo_complemento_1_busqueda": "REMI",
        "tipo_complemento_1": "Remision y/o Lista de Empaque",
        "numero_complemento_1": remi_number,
        "descripcion_complemento_1": "REMISION",
        "tipo_complemento_2_busqueda": "acu",
        "tipo_complemento_2": "Contrato o acuerdo comercial (cuando aplique)",
        "numero_complemento_2": contract_number,
        "descripcion_complemento_2": "CONTRATO",
        "archivo_remision": str(path.resolve()),
    }
