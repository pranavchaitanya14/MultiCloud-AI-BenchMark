# Metric weights and settings used by bench.py
WEIGHTS = {
    "latency": 0.45,      # lower is better
    "cost": 0.35,         # lower is better
    "success": 0.20       # higher is better
}

# Rough token estimator (characters per token). Adjust if needed.
CHARS_PER_TOKEN = 4

# Number of concurrent requests per provider during the run.
CONCURRENCY = 5

# Prompts used for the test set (keep short for fast runs; add your domain prompts later).
PROMPTS = [
    "Summarize: Cloud orchestration across AWS, Azure, and GCP for LLM inference.",
    "Explain the trade-offs between cost and latency for serving a 8B instruction-tuned model.",
    "Given a 500-token prompt, estimate throughput and memory requirements for vLLM on A10 GPU.",
    "Return a one-sentence definition of retrieval-augmented generation.",
    "Provide three bullet points comparing serverless vs. VM hosting for model inference."
]
