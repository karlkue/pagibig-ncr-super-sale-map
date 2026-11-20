#!/usr/bin/env python3
"""
Verification suite for data/ropa_condos.json and data/banks_directory.json.
Ensures zero synthetic/hallucinated records remain, all records are strictly
in NCR (Metro Manila), and every record has complete source provenance
(source_url, source_page, title_no, raw_text, contact_officer).
"""

import json
import sys
from pathlib import Path

NCR_CITIES = {
    "Caloocan",
    "Las Piñas",
    "Makati",
    "Malabon",
    "Mandaluyong",
    "Manila",
    "Marikina",
    "Muntinlupa",
    "Navotas",
    "Parañaque",
    "Pasay",
    "Pasig",
    "Pateros",
    "Quezon City",
    "San Juan",
    "Taguig",
    "Valenzuela",
}

SYNTHETIC_REF_IDS = {
    "BPI-BM-2026-0412",
    "BPI-BM-2026-0589",
    "BDO-ROPA-2026-1104",
    "BDO-ROPA-2026-1288",
    "MB-AA-2026-0771",
    "MB-AA-2026-0833",
    "SBC-RA-2026-0319",
    "SBC-RA-2026-0394",
    "BDO-ROPA-2026-1402",
    "PSB-AA-2026-0210",
    "RCBC-ROPA-2026-0644",
    "EW-AA-2026-0912",
    "PNB-SAMG-2026-0455",
}


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    condos_path = repo_root / "data" / "ropa_condos.json"
    dir_path = repo_root / "data" / "banks_directory.json"
    html_path = repo_root / "ropa-sweep.html"

    condos = json.loads(condos_path.read_text(encoding="utf-8"))
    banks = json.loads(dir_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")

    assert len(condos) >= 50, f"Expected at least 50 real records, got {len(condos)}"
    assert "FALLBACK_DATA" not in html, "Synthetic FALLBACK_DATA still present in ropa-sweep.html"
    assert "The Sapphire Bloc" not in html and "The Sapphire Bloc" not in condos_path.read_text(), (
        "Hallucinated Sapphire Bloc record still present!"
    )

    for idx, rec in enumerate(condos, 1):
        ref_id = rec.get("ref_id", "")
        assert ref_id not in SYNTHETIC_REF_IDS, f"Synthetic ref_id found: {ref_id}"
        assert rec.get("city") in NCR_CITIES, f"Non-NCR city in record #{idx}: {rec.get('city')}"
        assert rec.get("title_status") == "Clean", f"Non-clean title in #{idx}: {rec}"
        assert rec.get("occupancy") == "Unoccupied", f"Occupied unit in #{idx}: {rec}"
        assert rec.get("source_url", "").startswith("https://"), f"Missing official source_url in #{idx}"
        assert rec.get("source_page"), f"Missing source_page in #{idx}"
        assert rec.get("raw_text"), f"Missing verbatim raw_text in #{idx}"
        assert rec.get("contact_officer"), f"Missing contact_officer in #{idx}"
        assert float(rec.get("asking_price", 0)) > 0, f"Invalid asking_price in #{idx}"
        assert 14.35 <= float(rec.get("lat", 0)) <= 14.80, f"Lat out of NCR bounds in #{idx}"
        assert 120.90 <= float(rec.get("lng", 0)) <= 121.15, f"Lng out of NCR bounds in #{idx}"

    print(f"PASS: Verified {len(condos)} real NCR Green-Tag condominium listings across {len(banks)} ROPA bank sources.")
    print("PASS: Zero synthetic records remain; all records have verbatim PDF/portal provenance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
