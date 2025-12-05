import streamlit as st
import pandas as pd
from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]
results_csv = BASE / "results" / "results.csv"
summary_json = BASE / "results" / "summary.json"

st.set_page_config(page_title="Multi‑Cloud LLM Benchmark", layout="wide")

st.title("Multi‑Cloud LLM Benchmark — Minimal Dashboard")
st.caption("Side‑by‑side comparison of providers for a target model family/capability")

if results_csv.exists():
    df = pd.read_csv(results_csv)
    st.subheader("Overall Scores")
    st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
else:
    st.warning("No results yet. Run `python bench/bench.py` first.")

if summary_json.exists():
    data = json.loads(summary_json.read_text())
    st.subheader("Per‑provider metrics")
    st.json(data)
