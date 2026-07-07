"""Generate synthetic financial, budget, and traffic CSVs for the KPI report.

Deterministic given a seed. Produces the same three shapes the production
version reads from SAP + Excel + GA4.
"""
from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

# 6 brands, 6 countries, real currency spread — matches the production shape
BRANDS = [
    # brand_key,  country, currency, revenue_scale (relative size), betting_share
    ("brand_a",   "PT",    "EUR",    1.00, 0.55),
    ("brand_b",   "RS",    "RSD",    0.60, 0.70),
    ("brand_c",   "SK",    "EUR",    0.45, 0.35),
    ("brand_d",   "RO",    "RON",    0.80, 0.65),
    ("brand_e",   "NL",    "EUR",    0.35, 0.10),
    ("brand_f",   "BG",    "BGN",    0.50, 0.40),
]

# P&L lines — same rough structure as SAP FC1 output
PL_LINES = [
    ("Advertising Revenue",   "Revenue", 1.0),
    ("Betting Revenue",       "Revenue", 1.0),
    ("Subscription Revenue",  "Revenue", 1.0),
    ("Other Revenue",         "Revenue", 1.0),
    ("Personnel Costs",       "Costs",  -1.0),
    ("Content Costs",         "Costs",  -1.0),
    ("Technology Costs",      "Costs",  -1.0),
    ("Marketing Costs",       "Costs",  -1.0),
    ("Other Costs",           "Costs",  -1.0),
]

# Approx annual revenue in local currency for brand_a (EUR). All others scale from this.
BASE_ANNUAL_REVENUE_EUR = 3_000_000

# Rough currency conversion to EUR (for reference — the report converts to CHF downstream)
FX_TO_EUR = {"EUR": 1.0, "RSD": 0.0085, "RON": 0.20, "BGN": 0.51, "CHF": 1.05}


def month_iter(start: date, months: int):
    """Yield the first day of each month for `months` months starting at `start`."""
    y, m = start.year, start.month
    for _ in range(months):
        yield date(y, m, 1)
        m += 1
        if m > 12:
            m = 1
            y += 1


def seasonality(month: int) -> float:
    """Sports media: summer transfer window + autumn league starts = higher traffic + revenue."""
    return {1: 0.95, 2: 0.90, 3: 1.00, 4: 1.05, 5: 1.00, 6: 1.10,
            7: 1.15, 8: 1.20, 9: 1.15, 10: 1.10, 11: 1.05, 12: 0.95}[month]


@dataclass
class Row:
    def to_dict(self) -> dict: return self.__dict__


def gen_financial(months: list[date], seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for m in months:
        for brand_key, country, currency, revenue_scale, betting_share in BRANDS:
            base_monthly_rev = BASE_ANNUAL_REVENUE_EUR * revenue_scale / 12 * seasonality(m.month)
            in_local = base_monthly_rev / FX_TO_EUR[currency]

            for line_name, category, sign in PL_LINES:
                if category == "Revenue":
                    # split revenue across the 4 lines with the brand's betting share
                    if line_name == "Betting Revenue":
                        share = betting_share
                    elif line_name == "Advertising Revenue":
                        share = (1 - betting_share) * 0.75
                    elif line_name == "Subscription Revenue":
                        share = (1 - betting_share) * 0.20
                    else:  # Other
                        share = (1 - betting_share) * 0.05
                    amount = in_local * share * rng.uniform(0.85, 1.15)
                else:
                    # costs = fixed proportion of revenue with noise, then negated
                    cost_shares = {
                        "Personnel Costs":   0.35,
                        "Content Costs":     0.15,
                        "Technology Costs":  0.08,
                        "Marketing Costs":   0.12,
                        "Other Costs":       0.05,
                    }
                    amount = in_local * cost_shares[line_name] * rng.uniform(0.90, 1.10)

                rows.append({
                    "period": m.isoformat(),
                    "brand_key": brand_key,
                    "country": country,
                    "currency": currency,
                    "pl_line": line_name,
                    "pl_category": category,
                    "amount": round(amount * sign, 2),
                })
    # ponytail: drop ~1% of rows to simulate real-world messy exports
    keep = [r for r in rows if rng.random() > 0.01]
    return keep


def gen_budget(months: list[date], seed: int) -> list[dict]:
    """Budget = financial-shaped, but frozen once at year start, without noise."""
    rng = random.Random(seed + 1)
    rows = []
    for m in months:
        for brand_key, country, currency, revenue_scale, betting_share in BRANDS:
            base_monthly_rev = BASE_ANNUAL_REVENUE_EUR * revenue_scale / 12 * seasonality(m.month)
            in_local = base_monthly_rev / FX_TO_EUR[currency]
            # Budgets are typically slightly optimistic
            optimism = rng.uniform(1.02, 1.10)

            for line_name, category, sign in PL_LINES:
                if category == "Revenue":
                    if line_name == "Betting Revenue":
                        share = betting_share
                    elif line_name == "Advertising Revenue":
                        share = (1 - betting_share) * 0.75
                    elif line_name == "Subscription Revenue":
                        share = (1 - betting_share) * 0.20
                    else:
                        share = (1 - betting_share) * 0.05
                    amount = in_local * share * optimism
                else:
                    cost_shares = {
                        "Personnel Costs":   0.35,
                        "Content Costs":     0.15,
                        "Technology Costs":  0.08,
                        "Marketing Costs":   0.12,
                        "Other Costs":       0.05,
                    }
                    amount = in_local * cost_shares[line_name] * 0.98  # budgeted costs slightly leaner

                rows.append({
                    "period": m.isoformat(),
                    "brand_key": brand_key,
                    "country": country,
                    "currency": currency,
                    "pl_line": line_name,
                    "pl_category": category,
                    "amount": round(amount * sign, 2),
                })
    return rows


def gen_traffic(months: list[date], seed: int) -> list[dict]:
    """Daily traffic per brand per device. Weekend spikes + brand-size scaling + noise."""
    rng = random.Random(seed + 2)
    rows = []
    # Daily-user baseline per brand for brand_a. Numbers are illustrative — a
    # plausible sports-media range where brand_a peaks around 1.5M daily, other
    # brands scale down via revenue_scale.
    BASE_DAILY_USERS = 1_200_000
    for start_of_month in months:
        # iterate every day in that month
        y, mo = start_of_month.year, start_of_month.month
        next_mo = date(y + (mo // 12), (mo % 12) + 1, 1)
        d = start_of_month
        while d < next_mo:
            for brand_key, country, currency, revenue_scale, _ in BRANDS:
                base = BASE_DAILY_USERS * revenue_scale * seasonality(mo)
                weekend_lift = 1.25 if d.weekday() >= 5 else 1.0
                daily_users = int(base * weekend_lift * rng.uniform(0.85, 1.15))
                # sessions ~ 1.4× users, pageviews ~ 3.5× sessions — typical sports-media ratios
                for device, dev_share in [("mobile", 0.75), ("desktop", 0.20), ("tablet", 0.05)]:
                    users = int(daily_users * dev_share)
                    if users == 0: continue
                    # Real sports-media ratios: ~1.4 sessions/user, ~2 pageviews/session.
                    sessions = int(users * rng.uniform(1.3, 1.5))
                    pageviews = int(sessions * rng.uniform(1.8, 2.2))
                    rows.append({
                        "date": d.isoformat(),
                        "brand_key": brand_key,
                        "country": country,
                        "device": device,
                        "users": users,
                        "sessions": sessions,
                        "pageviews": pageviews,
                    })
            d += timedelta(days=1)
    # ponytail: 0.5% missing-day noise to prove downstream models handle gaps
    keep = [r for r in rows if rng.random() > 0.005]
    return keep


def write_csv(rows: list[dict], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        print(f"skipped {out_path} (no rows)")
        return
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out_path} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=24, help="how many months of data to generate")
    ap.add_argument("--seed", type=int, default=42, help="random seed (fixed = deterministic output)")
    ap.add_argument("--start", type=str, default="2024-07-01", help="first month, ISO date")
    ap.add_argument("--out", type=str, default="raw", help="output directory")
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    months = list(month_iter(start, args.months))
    out = Path(args.out)

    write_csv(gen_financial(months, args.seed), out / "financial" / f"{months[-1].isoformat()}_financial.csv")
    write_csv(gen_budget(months, args.seed),    out / "budget"    / f"{months[-1].isoformat()}_budget.csv")
    write_csv(gen_traffic(months, args.seed),   out / "traffic"   / f"{months[-1].isoformat()}_traffic.csv")


def demo():
    """Smoke test — regenerate deterministically and check row counts + seed stability."""
    start = date(2024, 7, 1)
    months = list(month_iter(start, 24))

    fin_a = gen_financial(months, seed=42)
    fin_b = gen_financial(months, seed=42)
    assert fin_a == fin_b, "seed 42 should be deterministic"

    fin_c = gen_financial(months, seed=43)
    assert fin_c != fin_a, "different seeds should produce different output"

    assert 1200 < len(fin_a) < 1350, f"expected ~1296 financial rows, got {len(fin_a)}"
    assert all(r["brand_key"] in {b[0] for b in BRANDS} for r in fin_a)

    bud = gen_budget(months, seed=42)
    assert 1290 <= len(bud) <= 1300, f"budget should be 1296 rows (24*6*9), got {len(bud)}"

    traf = gen_traffic(months, seed=42)
    # 24 months × ~30 days × 6 brands × 3 devices ≈ 12,960, minus 0.5% noise
    assert 12_800 < len(traf) < 13_200, f"expected ~13k traffic rows, got {len(traf)}"

    print(f"demo OK: {len(fin_a)} financial, {len(bud)} budget, {len(traf)} traffic")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        main()
