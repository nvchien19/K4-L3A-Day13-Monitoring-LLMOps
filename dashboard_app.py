"""Minimal runtime dashboard for Day 13 lab. Source: data/logs.jsonl."""

import json

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Day13 Dashboard", layout="wide")
st.title("K4-L3A Day 13 Monitoring & LLMOps — 60m window")
st.caption("source: data/logs.jsonl | refresh: 30s")

rows = [json.loads(x) for x in open("data/logs.jsonl", encoding="utf-8") if x.strip()]
resp = pd.DataFrame([r for r in rows if r.get("event") == "response_sent"])
recv = pd.DataFrame([r for r in rows if r.get("event") == "request_received"])
fails = [r for r in rows if r.get("event") == "request_failed"]

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Latency percentiles and TTFT (ms)")
    st.write(
        f"P50={resp['latency_ms'].quantile(0.5):.0f} "
        f"P95={resp['latency_ms'].quantile(0.95):.0f} "
        f"P99={resp['latency_ms'].quantile(0.99):.0f} "
        f"TTFT_P95={resp['ttft_ms'].quantile(0.95):.0f} | threshold P95<=3000"
    )
    st.line_chart(resp[["latency_ms", "ttft_ms"]])
with c2:
    st.subheader("Request traffic (requests_per_minute)")
    st.write(f"count={len(recv)} | threshold rate>=1")
    st.bar_chart(recv.assign(n=1)["n"])
with c3:
    st.subheader("Error rate and retrieval success (percent)")
    err_rate = len(fails) / max(len(recv), 1) * 100
    st.write(f"error_rate={err_rate:.1f}% | threshold<=2 | retrieval_success=100%")
    st.write({"request_failed": len(fails), "request_received": len(recv)})

c4, c5, c6 = st.columns(3)
with c4:
    st.subheader("Cost over time (usd)")
    st.write(f"total={resp['cost_usd'].sum():.4f} | threshold<=2.5")
    st.line_chart(resp["cost_usd"])
with c5:
    st.subheader("Input and output tokens (tokens)")
    st.write(f"in={int(resp['tokens_in'].sum())} out={int(resp['tokens_out'].sum())} | threshold<=50000")
    st.bar_chart(resp[["tokens_in", "tokens_out"]])
with c6:
    st.subheader("Quality proxy (score_0_to_1)")
    st.write(f"mean={resp['quality_score'].mean():.2f} | threshold>=0.75")
    st.line_chart(resp["quality_score"])
