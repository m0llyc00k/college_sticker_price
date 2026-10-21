#!/usr/bin/env python3
"""
public_cost_and_aid.py

In-state cost of attendance and average grant aid for the ENTIRE population of
public, bachelor's-granting U.S. colleges, from the College Scorecard API.

This is the "what does public college typically cost" pull: every public 4-year
school (not a top-N ranking), in-state figures, with the sticker-to-net drop.

Fields:
  * In-state cost of attendance = `cost.attendance.academic_year`.
    For PUBLIC schools this is already the in-state/in-district figure (it's
    built from in-state tuition + books + living costs).
  * In-state net price = `cost.avg_net_price.public` (IPEDS bases public net
    price on in-state students).
  * Average grant aid is NOT a Scorecard field, so it's DERIVED as
    aid = cost_of_attendance - net_price  (the IPEDS definition of net price).
    Caveat: net price is measured on first-time, full-time, Title IV aid
    recipients, so this average aid is for that cohort, not every student.
  * Undergrad enrollment is included so you can weight by student.

DATA YEAR: "latest." hides the year and cost data lags, so we probe explicit
years, take the newest non-null value per school, and record the year used.
COA and net price are taken from the SAME year per school so the derived aid is
internally consistent.

Setup:
    pip3 install requests
    export SCORECARD_API_KEY=your_key        (free at https://api.data.gov/signup)

Examples:
    python3 public_cost_and_aid.py
    python3 public_cost_and_aid.py --out public_cost_and_aid.csv
    python3 public_cost_and_aid.py --sort aid      # biggest discount first
"""

import argparse
import csv
import os
import sys
import time
from statistics import median, quantiles

import requests

API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
MAX_PER_PAGE = 100

# Years to probe, most recent first. Each integer Y means award year Y..Y+1.
CANDIDATE_YEARS = [2025, 2024, 2023, 2022, 2021, 2020]

IDENTITY_FIELDS = ["id", "school.name", "school.city", "school.state", "school.ownership"]

COA_BASE = "cost.attendance.academic_year"     # in-state COA for publics
NET_BASE = "cost.avg_net_price.public"          # in-state net price for publics
TUITION_BASE = "cost.tuition.in_state"
ENROLL_BASE = "student.size"

OWNERSHIP = {1: "Public", 2: "Private nonprofit", 3: "Private for-profit"}

# "What people assume public college costs," for the reality check.
BAND_LO, BAND_HI = 20000, 29000


def build_fields():
    fields = list(IDENTITY_FIELDS)
    for y in CANDIDATE_YEARS:
        for base in (COA_BASE, NET_BASE, TUITION_BASE, ENROLL_BASE):
            fields.append(f"{y}.{base}")
    return fields


def year_label(y):
    return f"{y}-{str(y + 1)[-2:]}"


def pick(row, base):
    """Most recent non-null value for `base`, plus the year it came from."""
    for y in CANDIDATE_YEARS:
        v = row.get(f"{y}.{base}")
        if v is not None and v != "":
            return v, year_label(y)
    return None, None


def pick_coa_and_net(row):
    """COA and net price from the SAME most-recent year that has BOTH populated,
    so the derived aid (COA - net) is consistent. Falls back to each field's own
    newest value if no single year has both."""
    for y in CANDIDATE_YEARS:
        coa = row.get(f"{y}.{COA_BASE}")
        net = row.get(f"{y}.{NET_BASE}")
        if coa not in (None, "") and net not in (None, ""):
            return coa, net, year_label(y)
    return None, None, None


def fetch_all(api_key, degree, ownership):
    """Page through ALL schools matching the indexed filters (no server sort)."""
    session = requests.Session()
    fields = ",".join(build_fields())
    rows, page = [], 0

    while True:
        params = {
            "fields": fields,
            "school.degrees_awarded.predominant": degree,  # indexed
            "school.ownership": ownership,                 # indexed
            "per_page": MAX_PER_PAGE,
            "page": page,
            "api_key": api_key,
        }
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
    """Resolve in-state COA + net (same year) and derive average aid."""
    out = []
    for r in rows:
        coa, net, year = pick_coa_and_net(r)
        if coa is None:
            continue  # need both COA and net to derive aid
        aid = coa - net
        tui, tui_year = pick(r, TUITION_BASE)
        enr, enr_year = pick(r, ENROLL_BASE)
        out.append({
            "name": r.get("school.name"),
            "city": r.get("school.city"),
            "state": r.get("school.state"),
            "coa": coa,
            "net": net,
            "aid": aid,
            "data_year": year,
            "tuition": tui, "tuition_year": tui_year,
            "enrollment": enr, "enrollment_year": enr_year,
        })
    return out


def weighted_median(pairs):
    data = sorted((v, w) for v, w in pairs if w)
    if not data:
        return None
    total = sum(w for _, w in data)
    acc = 0
    for v, w in data:
        acc += w
        if acc >= total / 2:
            return v
    return data[-1][0]


def med(vals):
    vals = [v for v in vals if v is not None]
    return int(median(vals)) if vals else None


def summarize(rows):
    n = len(rows)
    coa = [r["coa"] for r in rows]
    net = [r["net"] for r in rows]
    aid = [r["aid"] for r in rows]
    wmed_net = weighted_median([(r["net"], r["enrollment"]) for r in rows])
    q = quantiles(net, n=4) if n >= 4 else [None, None, None]

    below = sum(1 for v in net if v < BAND_LO)
    within = sum(1 for v in net if BAND_LO <= v <= BAND_HI)
    above = sum(1 for v in net if v > BAND_HI)

    print(f"\nPublic, bachelor's-granting colleges (in-state): {n}\n")
    print(f"  median cost of attendance : ${med(coa):,}")
    print(f"  median average aid        : ${med(aid):,}")
    print(f"  median net price          : ${med(net):,}")
    if wmed_net is not None:
        print(f"  median net (per student)  : ${int(wmed_net):,}   <- enrollment-weighted")
    if q[0] is not None:
        print(f"  net 25th / 75th pct       : ${int(q[0]):,} / ${int(q[2]):,}")
    print(f"\nNet price vs. the ${BAND_LO:,}-${BAND_HI:,} people assume:")
    print(f"  below ${BAND_LO:,} : {below:>4}  ({below/n:4.0%})")
    print(f"  {BAND_LO//1000}k-{BAND_HI//1000}k      : {within:>4}  ({within/n:4.0%})")
    print(f"  above ${BAND_HI:,} : {above:>4}  ({above/n:4.0%})")
    print()


def write_csv(rows, path):
    headers = [
        "name", "city", "state",
        "in_state_cost_of_attendance", "average_grant_aid", "in_state_net_price",
        "data_year",
        "in_state_tuition", "tuition_data_year",
        "undergrad_enrollment", "enrollment_data_year",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow([
                r["name"], r["city"], r["state"],
                r["coa"], r["aid"], r["net"],
                r["data_year"],
                r["tuition"], r["tuition_year"],
                r["enrollment"], r["enrollment_year"],
            ])


def main():
    p = argparse.ArgumentParser(
        description="In-state COA + average aid for all public 4-year colleges.")
    p.add_argument("--degree", type=int, default=3,
                   help="Predominant degree: 3=bachelor's (default), 4=graduate.")
    p.add_argument("--ownership", type=int, choices=[1, 2, 3], default=1,
                   help="1=public (default), 2=private nonprofit, 3=for-profit.")
    p.add_argument("--sort", choices=["net", "coa", "aid", "name"], default="net",
                   help="CSV row order (default 'net', cheapest first).")
    p.add_argument("--out", default="public_cost_and_aid.csv", help="Output CSV path.")
    p.add_argument("--api-key", default=os.environ.get("SCORECARD_API_KEY"),
                   help="API key (or set SCORECARD_API_KEY).")
    args = p.parse_args()

    if not args.api_key:
        sys.exit("No API key. Get one free at https://api.data.gov/signup, then "
                 "export SCORECARD_API_KEY=... or pass --api-key.")

    raw = fetch_all(args.api_key, args.degree, args.ownership)
    rows = enrich(raw)
    if not rows:
        sys.exit("No schools with both in-state COA and net price returned.")

    keymap = {"net": "net", "coa": "coa", "aid": "aid"}
    if args.sort == "name":
        rows.sort(key=lambda r: (r["name"] or ""))
    else:
        rows.sort(key=lambda r: r[keymap[args.sort]])

    write_csv(rows, args.out)
    summarize(rows)
    print(f"Wrote {len(rows)} schools to {args.out}")


if __name__ == "__main__":
    main()