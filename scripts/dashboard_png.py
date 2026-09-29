"""Generate a 6-panel dashboard PNG from data/logs.jsonl.

Contract source: config/dashboard.yaml (same panels, units, thresholds).
Usage: python scripts/dashboard_png.py [--out submission/evidence/11-dashboard-overview.png]
"""
from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"


def pct(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, round((p / 100) * len(ordered) + 0.5) - 1))
    return float(ordered[idx])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="submission/evidence/11-dashboard-overview.png")
    parser.add_argument("--title", default="K4-L3A Day 13 Monitoring & LLMOps")
    args = parser.parse_args()

    records = [json.loads(x) for x in LOG_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    resp = [r for r in records if r.get("event") == "response_sent"]
    recv = [r for r in records if r.get("event") == "request_received"]
    fail = [r for r in records if r.get("event") == "request_failed"]

    lat = [r.get("latency_ms", 0) for r in resp]
    ttft = [r.get("ttft_ms", 0) for r in resp]
    cost = [r.get("cost_usd", 0.0) for r in resp]
    tin = [r.get("tokens_in", 0) for r in resp]
    tout = [r.get("tokens_out", 0) for r in resp]
    qual = [r.get("quality_score", 0.0) for r in resp]
    ts = [r.get("ts", "") for r in records if r.get("ts")]

    p50, p95, p99 = pct(lat, 50), pct(lat, 95), pct(lat, 99)
    ttft_p95 = pct(ttft, 95)
    err_rate = (len(fail) / max(len(recv), 1)) * 100
    tool_ok = [r for r in resp if r.get("tool_success") is True]
    tool_known = [r for r in resp if r.get("tool_success") is not None]
    retr_success = (len(tool_ok) / max(len(tool_known), 1)) * 100
    total_cost = sum(cost)
    mean_qual = statistics.mean(qual) if qual else 0.0
    window = f"{min(ts)[:19]}Z .. {max(ts)[:19]}Z" if ts else "no data"

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f"{args.title} | time range: {window} | source: data/logs.jsonl", fontsize=13)
    (a_lat, a_traf, a_err), (a_cost, a_tok, a_qual) = axes

    x = list(range(1, len(resp) + 1))
    a_lat.plot(x, lat, marker="o", label="latency_ms")
    a_lat.plot(x, ttft, marker=".", label="ttft_ms")
    a_lat.axhline(3000, color="red", linestyle="--", label="threshold P95<=3000")
    a_lat.set_title(f"Latency percentiles and TTFT (ms)\nP50={p50:.0f} P95={p95:.0f} P99={p99:.0f} TTFT_P95={ttft_p95:.0f}")
    a_lat.set_xlabel("request #")
    a_lat.legend(fontsize=8)

    a_traf.bar(["request_received"], [len(recv)])
    a_traf.set_title(f"Request traffic (requests_per_minute)\ncount={len(recv)} | threshold rate>=1")
    a_traf.set_ylabel("count")

    a_err.bar(["error_rate_pct"], [err_rate])
    a_err.axhline(2, color="red", linestyle="--", label="threshold<=2")
    a_err.set_title(f"Error rate and retrieval success (percent)\nerror_rate={err_rate:.1f}% retrieval_success={retr_success:.1f}%")
    a_err.legend(fontsize=8)

    a_cost.plot(x, cost, marker="o")
    a_cost.axhline(2.5, color="red", linestyle="--", label="threshold total<=2.5")
    a_cost.set_title(f"Cost over time (usd)\ntotal={total_cost:.4f}")
    a_cost.set_xlabel("request #")
    a_cost.legend(fontsize=8)

    a_tok.bar(["tokens_in", "tokens_out"], [sum(tin), sum(tout)])
    a_tok.axhline(50000, color="red", linestyle="--", label="threshold<=50000")
    a_tok.set_title(f"Input and output tokens (tokens)\nin={sum(tin)} out={sum(tout)}")
    a_tok.legend(fontsize=8)

    a_qual.plot(x, qual, marker="o")
    a_qual.axhline(0.75, color="red", linestyle="--", label="threshold>=0.75")
    a_qual.set_title(f"Quality proxy (score_0_to_1)\nmean={mean_qual:.2f}")
    a_qual.set_xlabel("request #")
    a_qual.legend(fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    print(f"saved: {out} | requests={len(recv)} responses={len(resp)} fails={len(fail)}")


if __name__ == "__main__":
    main()
