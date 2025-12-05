from fastapi import FastAPI, Header
import httpx, time, yaml, os, random

app = FastAPI()
CONFIG_PATH = os.environ.get("PROVIDERS_CONFIG", "config/providers.yaml")

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# Simple in-memory health cache
health = {p["name"]: {"ok": True, "latency_ms": 500.0} for p in CONFIG["providers"]}

def choose_provider(policy: str = "best"):
    providers = CONFIG["providers"]
    if policy == "random":
        return random.choice(providers)
    # 'best' policy: pick provider with lowest observed latency and ok health
    healthy = [p for p in providers if health[p["name"]]["ok"]]
    pool = healthy or providers
    return min(pool, key=lambda p: health[p["name"]]["latency_ms"])

@app.get("/health")
def healthz():
    return {"status": "ok", "providers": list(health.keys())}

@app.post("/generate")
async def generate(payload: dict, x_policy: str | None = Header(default=None)):
    provider = choose_provider(x_policy or "best")
    ptype = provider["type"]
    start = time.perf_counter()
    try:
        if ptype == "mock":
            # simulate work
            mean = provider.get("mock_latency_ms_mean", 600)
            jitter = provider.get("mock_latency_ms_jitter", 150)
            success_rate = provider.get("mock_success_rate", 0.98)
            delay = max(50, random.gauss(mean, jitter)) / 1000.0
            await _async_sleep(delay)
            ok = random.random() <= success_rate
            if not ok:
                raise RuntimeError("mock failure")
            out = {"text": "mocked-response", "provider": provider["name"]}
        elif ptype == "http":
            headers = {}
            if "auth_header" in provider:
                k, v = provider["auth_header"].split(":", 1)
                headers[k.strip()] = v.strip()
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(provider["base_url"], json=payload, headers=headers)
                resp.raise_for_status()
                out = resp.json()
        else:
            raise ValueError(f"unknown provider type: {ptype}")
        elapsed = (time.perf_counter() - start) * 1000
        health[provider["name"]] = {"ok": True, "latency_ms": elapsed}
        return {"ok": True, "elapsed_ms": elapsed, "provider": provider["name"], "output": out}
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        health[provider["name"]] = {"ok": False, "latency_ms": elapsed}
        return {"ok": False, "elapsed_ms": elapsed, "provider": provider["name"], "error": str(e)}

async def _async_sleep(s: float):
    # tiny awaitable sleep without importing asyncio in global scope
    import asyncio
    await asyncio.sleep(s)
