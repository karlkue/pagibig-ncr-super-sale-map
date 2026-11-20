# pagibig-ncr-super-sale-map
Interactive map of Pag-IBIG NCR Super Sale (Negotiated Sale) properties, plus **Exercise #1: Q4 Commercial Bank ROPA "Failed-Bidding" Sweep**.

## Exercise #1: Q4 Commercial Bank ROPA "Failed-Bidding" Sweep
- **Interactive Map & Bid Generator**: Open `ropa-sweep.html` to filter **BPI Buena Mano**, **BDO**, **Metrobank**, and **Security Bank** for Green-Tag (clean title, unoccupied) condos with 2+ failed sealed bidding rounds, calculate 35%–50% lowball bids, and generate Q4 Oct–Nov Offer-to-Buy letters.
- **CLI Sweep & Letter Exporter**:
  ```bash
  python3 scripts/ropa_sweep.py --discount 45 --letters-dir out/letters
  ```
