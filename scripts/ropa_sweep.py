#!/usr/bin/env python3
"""
Q4 Commercial Bank ROPA "Failed-Bidding" Sweep (Exercise #1)
Filters BPI Buena Mano, BDO, Metrobank, and Security Bank for Green-Tag
(clean title, unoccupied) condos that have failed 2+ sealed bidding rounds,
calculates 35%-50% lowball bids, and generates Q4 Oct-Nov offer letters.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BANK_PORTALS = {
    "BPI Buena Mano": {
        "url": "https://www.buenamano.ph/",
        "department": "BPI Buena Mano - Asset Management & Disposal",
        "submission_note": "Submit Offer to Buy (OTB) form with 5% earnest money / manager's check.",
    },
    "BDO": {
        "url": "https://www.bdo.com.ph/personal/assets-for-sale/real-estate",
        "department": "BDO Unibank - Acquired Assets Management Group",
        "submission_note": "Submit Offer to Purchase (OTP) via BDO Acquired Assets portal or disposal officer.",
    },
    "Metrobank": {
        "url": "https://www.metrobank.com.ph/assets-for-sale/properties",
        "department": "Metrobank - Acquired Assets Disposal Division",
        "submission_note": "Submit Acquired Assets Offer to Buy Form + Buyer's Profile.",
    },
    "Security Bank": {
        "url": "https://www.securitybank.com/personal/loans/repossessed-assets/properties-for-sale/",
        "department": "Security Bank - Repossessed Assets Management",
        "submission_note": "Submit Sealed Bid / Negotiated Offer form for re-offered ROPA.",
    },
    "PSBank": {
        "url": "https://www.psbank.com.ph/properties-for-sale/",
        "department": "PSBank - Acquired Assets Management",
        "submission_note": "Submit Offer to Buy via PSBank Asset Management.",
    },
    "RCBC": {
        "url": "https://www.rcbc.com/rcbc-properties-for-sale",
        "department": "RCBC - Asset Management & Remedial Group",
        "submission_note": "Submit Offer to Purchase (OTP) for bank-owned property.",
    },
    "EastWest Bank": {
        "url": "https://www.eastwestbanker.com/investments/acquired-assets/pre-owned-properties",
        "department": "EastWest Bank - Acquired Assets Division",
        "submission_note": "Submit Offer to Buy via EastWest Acquired Assets.",
    },
    "PNB": {
        "url": "https://www.pnb.com.ph/index.php/acquired-assets",
        "department": "PNB - Special Assets Management Group",
        "submission_note": "Submit Sealed Bid / Negotiated Sale Offer.",
    },
}


def calculate_lowball_bids(asking_price: float) -> Dict[str, float]:
    """Calculate 35% to 50% lowball bid range (50% to 65% of asking price)."""
    return {
        "discount_35_bid": round(asking_price * 0.65, 2),
        "discount_42_bid": round(asking_price * 0.58, 2),
        "discount_50_bid": round(asking_price * 0.50, 2),
    }


def is_green_tag_condo(prop: Dict[str, Any], min_failed_rounds: int = 2) -> bool:
    """
    Exercise #1 Filter:
    - Property Type: Condominium
    - Green-Tag: Clean Title (CCT ready, no lis pendens/adverse claim) AND Unoccupied
    - Failed Bidding: 2+ failed sealed bidding rounds
    """
    prop_type = str(prop.get("property_type", "")).lower()
    title_status = str(prop.get("title_status", "")).lower()
    occupancy = str(prop.get("occupancy", "")).lower()
    failed_rounds = int(prop.get("failed_bidding_rounds", 0))

    is_condo = "condo" in prop_type
    is_clean = title_status in ("clean", "green", "cct ready", "consolidated")
    is_unoccupied = occupancy in ("unoccupied", "vacant")
    has_failed_rounds = failed_rounds >= min_failed_rounds

    return is_condo and is_clean and is_unoccupied and has_failed_rounds


def generate_bid_letter(prop: Dict[str, Any], discount_pct: float = 45.0) -> str:
    """Generate a Q4 Oct-Nov lowball bid offer letter for bank disposal officers."""
    bank = prop.get("bank", "Commercial Bank")
    portal_info = BANK_PORTALS.get(bank, {})
    dept = portal_info.get("department", f"{bank} - Acquired Assets Department")
    asking = float(prop.get("asking_price", 0))
    bid_amount = round(asking * (1.0 - discount_pct / 100.0), 2)
    today = datetime.now().strftime("%B %d, %Y")

    return f"""Date: {today}
To: {dept}
Subject: Q4 Negotiated Offer to Buy — {prop.get('property_name', 'Condominium Unit')} (Ref: {prop.get('ref_id', 'N/A')})

Dear Disposal Officer,

I am writing to submit a formal, cash-backed Offer to Buy for the following Green-Tag (clean title, unoccupied) condominium unit currently in your ROPA inventory:

  • Property: {prop.get('property_name', 'N/A')}
  • Location: {prop.get('address', 'N/A')}, {prop.get('city', 'Metro Manila')}
  • Floor Area: {prop.get('floor_area_sqm', 'N/A')} sqm
  • Reference / Title No.: {prop.get('ref_id', 'N/A')}
  • Listed Asking Price: PHP {asking:,.2f}
  • Prior Sealed Bidding Rounds: {prop.get('failed_bidding_rounds', 2)}+ failed rounds

Given that this asset has remained in inventory following multiple sealed bidding rounds, I am submitting a firm Q4 negotiated offer of:

  >>> OFFER PRICE: PHP {bid_amount:,.2f} ({discount_pct:.0f}% below listed price) <<<

Key Terms for Fast Year-End Closing:
  1. Payment Terms: Cash / Manager's Check (or pre-approved bank financing) ready for immediate closing before year-end.
  2. Condition: "As-Is, Where-Is" basis; no contingencies on unit repairs.
  3. Timeline: Ready to submit earnest money deposit within 48 hours of offer acceptance.

Please let me know if we can proceed with formal documentation ({portal_info.get('submission_note', 'Offer to Buy form')}).

Sincerely,
[Your Name]
[Your Contact Number / Email]
"""


def load_properties(input_path: Path) -> List[Dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() == ".json":
        with input_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    elif input_path.suffix.lower() == ".csv":
        with input_path.open("r", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exercise #1: Q4 Commercial Bank ROPA Failed-Bidding Sweep"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "ropa_condos.json",
        help="Path to ROPA properties JSON or CSV file",
    )
    parser.add_argument(
        "--min-failed-rounds",
        type=int,
        default=2,
        help="Minimum number of failed sealed bidding rounds (default: 2)",
    )
    parser.add_argument(
        "--discount",
        type=float,
        default=45.0,
        help="Target lowball discount percentage between 35 and 50 (default: 45)",
    )
    parser.add_argument(
        "--letters-dir",
        type=Path,
        default=None,
        help="Optional directory to export generated Q4 bid offer letters (.txt)",
    )
    args = parser.parse_args()

    properties = load_properties(args.input)
    matches = [p for p in properties if is_green_tag_condo(p, args.min_failed_rounds)]

    print(f"Loaded {len(properties)} ROPA records from {args.input.name}")
    print(f"Found {len(matches)} Green-Tag Condos with {args.min_failed_rounds}+ failed bidding rounds:\n")

    for idx, prop in enumerate(matches, 1):
        asking = float(prop.get("asking_price", 0))
        bids = calculate_lowball_bids(asking)
        print(
            f"{idx}. [{prop.get('bank')}] {prop.get('property_name')} ({prop.get('city')})\n"
            f"   Ref: {prop.get('ref_id')} | Area: {prop.get('floor_area_sqm')} sqm | "
            f"Failed Rounds: {prop.get('failed_bidding_rounds')}x\n"
            f"   Asking: PHP {asking:,.0f} -> "
            f"35% off: PHP {bids['discount_35_bid']:,.0f} | "
            f"50% off: PHP {bids['discount_50_bid']:,.0f}\n"
        )

    if args.letters_dir and matches:
        args.letters_dir.mkdir(parents=True, exist_ok=True)
        for prop in matches:
            safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(prop.get("ref_id", "unit")))
            out_file = args.letters_dir / f"bid_letter_{safe_ref}.txt"
            out_file.write_text(generate_bid_letter(prop, args.discount), encoding="utf-8")
        print(f"Exported {len(matches)} Q4 bid offer letters to {args.letters_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
