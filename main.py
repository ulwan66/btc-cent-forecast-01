#!/usr/bin/env python3
"""btc-cent-forecast-01: forecast Bitcoin's US-dollar price 240 minutes ahead.

For each case file /input/<id>.in holding 4,320 one-minute closes of the
72 hours up to a checkpoint, write /output/<id>.out with one guess of the
close 240 minutes after the checkpoint.

Model: the honest middle estimate under mean absolute error is the
conditional median of the future price. Bitcoin's pool price here is close
to a random walk at a 4-hour horizon, so the last close carries most of the
signal -- but the variance of k-minute moves grows slower than k at
multi-hour scales in the practice data, i.e. the price partly reverts
toward its recent level. The forecast is therefore the last close pulled
one fifth of the way toward the median of the last 12 hours of closes:

    guess = last + 0.20 * (median(last 720 closes) - last)

The median anchor is robust to the pool's occasional one-minute spikes,
and the pull is small enough that a genuinely trending market is barely
penalised. No parameter is fitted to the answers: the anchor window and
the pull weight were chosen on the shape of the variance signature, and
the program is deterministic -- no randomness, no clock, no network --
so two runs on the same case write the same bytes.

Standard library only. Reads $MAKEFUN_INPUT_DIR (else /input) and writes
$MAKEFUN_OUTPUT_DIR (else /output), one output per *.in file, in name
order.
"""

import json
import math
import os
import statistics
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"

# The scorer's price bounds: finite, greater than 0, less than 10,000,000.
# Prices are carried as integer units of 1e-5 dollars so the emitted JSON
# always shows exactly five decimals and never a binary float artefact.
MIN_UNITS = 1  # 0.00001
MAX_UNITS = 999_999_999_999  # 9,999,999.99999
FALLBACK_UNITS = 100_000  # 1.00000, used only for unusable input

# How much of the gap between the last close and the 12-hour median close
# the forecast closes. Small on purpose: the random-walk part dominates.
REVERSION_WEIGHT = 0.20
# Anchor window in minutes: the last 12 hours of closes.
ANCHOR_MINUTES = 720


def grid_units(x):
    """Clamp x into the scorer's bounds and round to 5 decimals, as units."""
    if not math.isfinite(x):
        return FALLBACK_UNITS
    v = min(MAX_UNITS / 1e5, max(MIN_UNITS / 1e5, x))
    return max(MIN_UNITS, min(MAX_UNITS, int(math.floor(v * 1e5 + 0.5))))


def format_units(units):
    """Render integer 1e-5 units as a plain decimal with 5 places."""
    return f"{units // 100_000}.{units % 100_000:05d}"


def forecast(prices):
    """One price forecast, in 1e-5 units, from closes ending at the checkpoint."""
    closes = [p for p in prices if isinstance(p, (int, float)) and math.isfinite(p)]
    if not closes:
        return FALLBACK_UNITS
    last = closes[-1]
    anchor = statistics.median(closes[-ANCHOR_MINUTES:])
    return grid_units(last + REVERSION_WEIGHT * (anchor - last))


def case_guess(case_doc):
    """Forecast, in 1e-5 units, for one parsed case document."""
    markets = case_doc.get("markets") if isinstance(case_doc, dict) else None
    if isinstance(markets, list):
        for market in markets:
            if isinstance(market, dict) and isinstance(market.get("prices"), list):
                return forecast(market["prices"])
    return FALLBACK_UNITS


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        names = sorted(n for n in os.listdir(INPUT_DIR) if n.endswith(".in"))
    except OSError as exc:
        print(f"cannot list input dir {INPUT_DIR}: {exc}", file=sys.stderr)
        return 1
    for name in names:
        case_id = name[: -len(".in")]
        path = os.path.join(INPUT_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                doc = json.load(fh)
            units = case_guess(doc)
        except Exception as exc:  # never crash a case: fall back to a valid guess
            print(f"warning: {name}: {exc}; falling back", file=sys.stderr)
            units = FALLBACK_UNITS
        line = (
            '{"forecasts":[{"case":'
            + json.dumps(case_id)
            + ',"price":'
            + format_units(units)
            + "}]}\n"
        )
        out_path = os.path.join(OUTPUT_DIR, case_id + ".out")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
