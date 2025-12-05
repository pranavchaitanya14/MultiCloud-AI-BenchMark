import asyncio, time, yaml, json, os, statistics
import httpx, random, math, pandas as pd
from pathlib import Path
from bench.config import WEIGHTS, CHARS_PER_TOKEN, CONCURRENCY, PROMPTS

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load(open(BASE_DIR / "config" / "providers.yaml"))
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

async def invoke(client, provider, prompt):
    start = time.perf_counter()
    payload = {"prompt": prompt, "max_tokens": 64}
    try:
        if provider["type"] == "mock":
            # emulate orchestrator behavior to keep it self-contained
            mean = provider.get("mock_latency_ms_mean", 600)
            jitter = provider.get("mock_latency_ms_jitter", 150)
            success_rate = provider.get("mock_success_rate", 0.98)
            delay = max(50, random.gauss(mean, jitter)) / 1000.0
            await asyncio.sleep(delay)
            ok = random.random() <= success_rate
            if not ok:
                raise RuntimeError("mock failure")
            text = "mocked-response"
        else:
            headers = {}
            if "auth_header" in provider:
                k, v = provider["auth_header"].split(":", 1)
                headers[k.strip()] = v.strip()
            resp = await client.post(provider["base_url"], json=payload, headers=headers)
            resp.raise_for_status()
            js = resp.json()
            text = js.get("text") or str(js)[:200]
        elapsed_ms = (time.perf_counter() - start) * 1000
        tokens_in = max(1, math.ceil(len(prompt) / CHARS_PER_TOKEN))
        tokens_out = max(1, math.ceil(len(text) / CHARS_PER_TOKEN))
        price = provider.get("price_per_1k_tokens", 0.5)
        est_cost = price * (tokens_in + tokens_out) / 1000.0
        return {"ok": True, "latency_ms": elapsed_ms, "cost": est_cost}
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {"ok": False, "latency_ms": elapsed_ms, "cost": 0.0, "error": str(e)}

async def run_provider(provider):
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = []
        for _ in range(CONCURRENCY):
            for prompt in PROMPTS:
                tasks.append(invoke(client, provider, prompt))
        for coro in asyncio.as_completed(tasks):
            results.append(await coro)
    return results

def score_providers(rows):
    # Normalize: lower latency/cost is better; success is higher is better.
    latencies = [r["p50_latency_ms"] for r in rows]
    costs = [r["avg_cost"] for r in rows]
    succs = [r["success_rate"] for r in rows]

    min_lat, max_lat = min(latencies), max(latencies)
    min_cost, max_cost = min(costs), max(costs)

    def norm_low(x, xmin, xmax):
        if xmax == xmin:
            return 1.0
        # scaled to [0,1], 1 is best
        return (xmax - x) / (xmax - xmin)

    out = []
    for r in rows:
        nlat = norm_low(r["p50_latency_ms"], min_lat, max_lat)
        ncost = norm_low(r["avg_cost"], min_cost, max_cost)
        nsucc = r["success_rate"]  # already in [0,1]
        composite = 100 * (WEIGHTS["latency"] * nlat + WEIGHTS["cost"] * ncost + WEIGHTS["success"] * nsucc)
        r["score"] = round(composite, 2)
        out.append(r)
    return out

def summarize(provider_name, results):
    lat_ok = [x["latency_ms"] for x in results if x["ok"]]
    success = sum(1 for x in results if x["ok"]) / len(results) if results else 0.0
    avg_cost = sum(x["cost"] for x in results) / max(1, len(results))
    p50 = statistics.median(lat_ok) if lat_ok else float("inf")
    p95 = (statistics.quantiles(lat_ok, n=100)[94] if len(lat_ok) >= 20 else max(lat_ok) if lat_ok else float("inf"))
    return {
        "provider": provider_name,
        "p50_latency_ms": round(p50, 2) if p50 != float("inf") else None,
        "p95_latency_ms": round(p95, 2) if p95 != float("inf") else None,
        "success_rate": round(success, 3),
        "avg_cost": round(avg_cost, 6),
    }

def main():
    providers = CONFIG["providers"]
    all_rows = []
    for p in providers:
        print(f"Running: {p['name']}")
        results = asyncio.run(run_provider(p))
        row = summarize(p["name"], results)
        all_rows.append(row)

    scored = score_providers(all_rows)

    # Save CSV
    df = pd.DataFrame(scored)
    csv_path = RESULTS_DIR / "results.csv"
    df.to_csv(csv_path, index=False)

    # Save JSON
    json_path = RESULTS_DIR / "summary.json"
    with open(json_path, "w") as f:
        json.dump(scored, f, indent=2)

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")

if __name__ == "__main__":
    main()
