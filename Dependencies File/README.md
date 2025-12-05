# Multi‑Cloud LLM Orchestration — Minimal Implementation (Starter Kit)

This starter kit lets you do a *minimal* end‑to‑end experiment to compare cloud providers side‑by‑side
and show a dashboard of scores. You can run it in **mock mode** to generate publishable results immediately,
and later switch to **real endpoints** when you deploy on AWS/Azure/GCP.

## What you get

- `bench/bench.py` — concurrent runner that hits providers simultaneously and measures latency, success rate,
  and an estimated cost per 1K tokens. Produces `results/results.csv` and `results/summary.json`.
- `dashboard/streamlit_app.py` — a simple dashboard you can run locally or host to visualize the scores.
- `config/providers.yaml` — declare providers. Works with `type: mock` for instant results, or `type: http`
  to call your real endpoints (Bedrock, Azure OpenAI, Vertex AI, vLLM, etc.).
- `orchestrator/app.py` — a tiny FastAPI router that can round‑robin or choose the “best” provider on the fly.
- Infra stubs for Cloud Run (GCP), App Runner (AWS), and Azure Container Apps, so you can deploy the *same container*
  to all three clouds and compare fairly.

## Quickstart (Local, Mock Mode — produces real CSV + dashboard)

1) Create a Python venv (3.10+), then:
```
pip install -r requirements.txt
```
2) Run the benchmark (uses mock providers by default):
```
python bench/bench.py
```
3) Launch the dashboard:
```
streamlit run dashboard/streamlit_app.py
```
4) Open the Streamlit URL to view per‑cloud latency, cost, success rate, and overall score.

## Switching to Real Providers

Edit `config/providers.yaml` and replace any `type: mock` entries with `type: http` entries, e.g.:

```yaml
providers:
  - name: aws-bedrock-llama31
    type: http
    base_url: https://your-bedrock-proxy-or-endpoint/invoke
    auth_header: "x-api-key: YOUR_KEY"
    price_per_1k_tokens: 0.60
```

Add Azure and GCP similarly. Use the *same* model family everywhere for a fair comparison (e.g., Llama 3.1 8B via vLLM),
or declare a “capability tag” (e.g., 8B‑Instruct) and compare providers that host that tag.

## Minimal Deployment Pattern (Same container on all clouds)

Build one image from this repo (contains the FastAPI orchestrator):

```
docker build -t yourrepo/multicloud-orchestrator:latest .
docker push yourrepo/multicloud-orchestrator:latest
```

### GCP — Cloud Run
```
gcloud run deploy multicloud-orchestrator   --image=yourrepo/multicloud-orchestrator:latest   --region=us-central1 --allow-unauthenticated
```

### AWS — App Runner
```
aws apprunner create-service --service-name multicloud-orchestrator   --source-configuration ImageRepository={"ImageIdentifier"="yourrepo/multicloud-orchestrator:latest","ImageRepositoryType"="ECR_PUBLIC"},AutoDeploymentsEnabled=true
```

### Azure — Container Apps
```
az containerapp up -n multicloud-orchestrator -g YOUR_RG   --image yourrepo/multicloud-orchestrator:latest --target-port 8000
```

Once deployed, set these service URLs as `base_url` entries in `config/providers.yaml` and re‑run `bench/bench.py`.

## Paper‑ready scoring

The runner normalizes metrics and computes a single score per provider (0–100). You can export both raw numbers and
the composite score for your paper’s tables/figures. Tweak the weights in `bench/config.py`.

---

**Note**: This kit focuses on *measurement orchestration*. It does not ship any model weights. To make an apples‑to‑apples
comparison with *identical* models, deploy an open model (e.g., Llama 3.1 8B Instruct) via **vLLM** to each cloud as
a container (Cloud Run / App Runner / Container Apps) and point the HTTP providers here to those endpoints.
