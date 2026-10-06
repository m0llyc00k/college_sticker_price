#!/usr/bin/env python3
"""
most_expensive_colleges.py

Rank U.S. colleges by cost of attendance using the U.S. Department of
Education's College Scorecard API (which serves IPEDS-reported cost data).

DATA YEAR: The Scorecard "latest." prefix hides which year each field is from,
and cost of attendance lags the file year. So this script requests several
explicit years, takes the most recent non-null value per school, and RECORDS
THE ACTUAL YEAR each figure came from in its own CSV column.

API QUIRK: Scorecard only sorts/range-filters on indexed fields, and cost of
attendance isn't one. So we filter on predominant degree (indexed), pull all
matching schools, and sort by cost in Python.

Setup:
    pip3 install requests
    Get a free key at https://api.data.gov/signup
    export SCORECARD_API_KEY=your_key_here     (or pass --api-key)

Examples:
    python3 most_expensive_colleges.py
    python3 most_expensive_colleges.py --top 200 --out costs.csv
    python3 most_expensive_colleges.py --min-cost 90000 --ownership 2
"""

import argparse
import csv
import os
import sys
import time

import requests

API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
MAX_PER_PAGE = 100  # College Scorecard hard cap

# Years to probe, most recent first. Each integer Y means award year Y..Y+1.
CANDIDATE_YEARS = [2025, 2024, 2023, 2022, 2021, 2020]

IDENTITY_FIELDS = ["id", "school.name", "school.city", "school.state", "school.ownership"]
COA_BASE = "cost.attendance.academic_year"
TUITION_BASE = "cost.tuition.out_of_state"
NETPRICE_BASES = ["cost.avg_net_price.private", "cost.avg_net_price.public"]
OWNERSHIP = {1: "Public", 2: "Private nonprofit", 3: "Private for-profit"}


def build_fields():
    fields = list(IDENTITY_FIELDS)
    for y in CANDIDATE_YEARS:
        fields.append(f"{y}.{COA_BASE}")
        fields.append(f"{y}.{TUITION_BASE}")
        for nb in NETPRICE_BASES:
            fields.append(f"{y}.{nb}")
    return fields


def year_label(y):
    return f"{y}-{str(y + 1)[-2:]}"  # 2023 -> "2023-24"


def pick(row, base):
    """Most recent non-null value for `base`, plus the year it came from."""
    for y in CANDIDATE_YEARS:
        v = row.get(f"{y}.{base}")
        if v is not None and v != "":
            return v, year_label(y)
    return None, None


def pick_net_price(row):
    """Net price uses two sub-fields (private/public); take the newest populated."""
    for y in CANDIDATE_YEARS:
        for nb in NETPRICE_BASES:
            v = row.get(f"{y}.{nb}")
            if v is not None and v != "":
                return v, year_label(y)
    return None, None


def fetch_all(api_key, degree, ownership):
    """Page through ALL schools matching an indexed filter (no server sort)."""
    session = requests.Session()
    fields = ",".join(build_fields())
    rows = []
    page = 0

    while True:
        params = {
            "fields": fields,
            "school.degrees_awarded.predominant": degree,  # indexed -> filterable
            "per_page": MAX_PER_PAGE,
            "page": page,
            "api_key": api_key,
        }
        if ownership:
            params["school.ownership"] = ownership  # also indexed

        resp = session.get(API_URL, params=params, timeout=30)
        if resp.status_code == 429:
            sys.stderr.write("Rate limited (1,000/hour). Waiting 60s...\n")
            time.sleep(60)
            continue
        if resp.status_code != 200:
            sys.exit(f"API error {resp.status_code}: {resp.text}")

        payload = resp.json()
        batch = payload.get("results", [])
        rows.extend(batch)

        total = payload.get("metadata", {}).get("total", 0)
        got = (page + 1) * MAX_PER_PAGE
        sys.stderr.write(f"\rFetched {min(got, total)} / {total} schools...")
        sys.stderr.flush()

        if not batch or got >= total:
            break
        page += 1
        time.sleep(0.25)

    sys.stderr.write("\n")
    return rows


def enrich(rows):
    """Resolve each school's newest cost/net-price/tuition value and its year."""
    out = []
    for r in rows:
        coa, coa_year = pick(r, COA_BASE)
        if coa is None:
            continue  # no reported cost of attendance -> can't rank it
        net, net_year = pick_net_price(r)
        tui, tui_year = pick(r, TUITION_BASE)
        out.append({
            "name": r.get("school.name"),
            "city": r.get("school.city"),
            "state": r.get("school.state"),
            "ownership": OWNERSHIP.get(r.get("school.ownership"), r.get("school.ownership")),
            "coa": coa, "coa_year": coa_year,
            "net": net, "net_year": net_year,
            "tuition": tui, "tuition_year": tui_year,
        })
    return out


def write_csv(rows, path, start_rank=1):
    headers = [
        "rank", "name", "city", "state", "ownership",
        "cost_of_attendance", "coa_data_year",
        "avg_net_price", "net_price_data_year",
        "tuition_out_of_state", "tuition_data_year",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for i, r in enumerate(rows, start_rank):
            w.writerow([
                i, r["name"], r["city"], r["state"], r["ownership"],
                r["coa"], r["coa_year"],
                r["net"], r["net_year"],
                r["tuition"], r["tuition_year"],
            ])


def main():
    p = argparse.ArgumentParser(description="Rank colleges by cost of attendance.")
    p.add_argument("--top", type=int, default=50, help="How many schools (default 50).")
    p.add_argument("--skip", type=int, default=0,
                   help="Skip this many top schools first (e.g. --skip 100 --top 100 = ranks 101-200).")
    p.add_argument("--min-cost", type=int, default=0,
                   help="Drop schools below this COA (default 0 = keep all).")
    p.add_argument("--degree", type=int, default=3,
                   help="Predominant degree: 3=bachelor's, 4=graduate (default 3).")
    p.add_argument("--ownership", type=int, choices=[1, 2, 3], default=None,
                   help="Filter: 1=public, 2=private nonprofit, 3=for-profit.")
    p.add_argument("--out", default="most_expensive_colleges.csv", help="Output CSV path.")
    p.add_argument("--api-key", default=os.environ.get("SCORECARD_API_KEY"),
                   help="API key (or set SCORECARD_API_KEY).")
    args = p.parse_args()

    if not args.api_key:
        sys.exit("No API key. Get one free at https://api.data.gov/signup, then "
                 "export SCORECARD_API_KEY=... or pass --api-key.")

    raw = fetch_all(args.api_key, args.degree, args.ownership)
    rows = enrich(raw)
    rows = [r for r in rows if r["coa"] >= args.min_cost]
    rows.sort(key=lambda r: r["coa"], reverse=True)
    rows = rows[args.skip:args.skip + args.top]

    if not rows:
        sys.exit("No results in that range. Try a smaller --skip or --min-cost 0.")

    start_rank = args.skip + 1
    write_csv(rows, args.out, start_rank)

    years = sorted({r["coa_year"] for r in rows}, reverse=True)
    print(f"\nWrote {len(rows)} schools (ranks {start_rank}-{args.skip + len(rows)}) to {args.out}")
    print(f"Cost-of-attendance data year(s) in these results: {', '.join(years)}\n")
    print(f"{'#':>3}  {'School':<38} {'COA':>9} {'yr':>7} {'Net':>9}")
    print("-" * 72)
    for i, r in enumerate(rows[:15], start_rank):
        name = (r["name"] or "")[:38]
        net = r["net"] or 0
        print(f"{i:>3}  {name:<38} {r['coa']:>9,} {r['coa_year']:>7} {net:>9,}")


if __name__ == "__main__":
    main()