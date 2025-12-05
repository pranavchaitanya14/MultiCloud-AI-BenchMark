# MultiCloud-AI-BenchMark
Each cloud offers different strengths for AI tasks, so the best model depends on the use case. This project benchmarks models from Azure OpenAI and AWS Bedrock using the same prompt to compare speed, reliability, and output quality. Results are stored and visualized through a Streamlit dashboard for clear performance comparison.



## **1️⃣ Switch from Windows PowerShell to Ubuntu (WSL)**

Open PowerShell and start Ubuntu:

```powershell
bash
```

---

## **2️⃣ Create project folder & extract ZIP (or create files manually)**

```bash
cd /mnt/c/Users/HP
mkdir multicloud-ai-benchmark
cd multicloud-ai-benchmark
```

If using a ZIP file:

```bash
cd /mnt/c/Users/HP/Downloads
sudo apt install unzip -y
unzip multicloud-ai-benchmark.zip -d /mnt/c/Users/HP/
```

---

## **3️⃣ Install Python and all dependencies**

```bash
sudo apt update && sudo apt install -y python3-pip
cd /mnt/c/Users/HP/multicloud-ai-benchmark
pip3 install -r requirements.txt
```

---

## **4️⃣ Deploy Azure OpenAI Model**

### 4.1 Create Azure OpenAI resource

1. Go to **Azure Portal**
2. Search **“Azure OpenAI” → Create**
3. Select subscription, resource group, region
4. Click **Review + Create → Create**

### 4.2 Deploy a model

1. Open **Azure OpenAI resource**
2. **Model Deployments → + Create**
3. Choose **gpt-35-turbo** (or other)
4. Deployment name: `gpt-35-turbo`
5. Click **Create**

### 4.3 Get endpoint + API key

In your Azure OpenAI resource:

* Go to **Keys and Endpoint**
* Copy **Endpoint** and **Key 1**

Set environment variable (recommended):

```bash
export AZURE_OPENAI_API_KEY="your_azure_openai_key"
```

### 4.4 Curl test (to validate deployment)

```bash
time curl -X POST \
  "https://<your-resource>.cognitiveservices.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2025-01-01-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

Replace `<your-resource>` with your Azure resource name.

---

## **5️⃣ Deploy AWS Bedrock Model**

### 5.1 Enable model access

1. AWS Console → **Amazon Bedrock**
2. **Model access → Manage model access**
3. Choose models (e.g., Claude 3 / Titan)
4. Click **Request access** → Wait until **Approved**

### 5.2 IAM JSON policy (copy/paste into AWS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    }
  ]
}
```

### 5.3 Create IAM user/role

1. IAM → **Users → Create user**
2. Enable **Programmatic access**
3. Attach the policy above
4. Download:

   * **Access key ID**
   * **Secret access key**

### 5.4 Configure AWS credentials on WSL

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"
```

Test Bedrock access:

```bash
aws bedrock list-foundation-models --region us-east-1
```


---

## **7️⃣ Configure Cloud Providers — `providers.yaml`**

Create folder **`config`** and inside it create **`providers.yaml`**:

```yaml
providers:
  - name: "Azure-OpenAI"
    type: "azure-openai"
    endpoint: "https://<your-azure-resource>.cognitiveservices.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2025-01-01-preview"
    api_key_env: "AZURE_OPENAI_API_KEY"
    price_per_1k_tokens: 0.00

  - name: "AWS-Bedrock"
    type: "aws-bedrock"
    region: "us-east-1"
    model_id: "anthropic.claude-3-opus-20240229"
    price_per_1k_tokens: 0.00
```

Replace values with your Azure resource and Bedrock model ID.

---

## **8️⃣ Run the Multicloud Benchmark**

From project root:

```bash
cd /mnt/c/Users/HP/multicloud-ai-benchmark
python3 -m bench.bench
```

This will:

* Read `providers.yaml`
* Send prompt to Azure + AWS
* Measure:

  * latency
  * success/failure
* Save output into `/results`:

  * `results.csv`
  * `summary.json`

---

## **9️⃣ Launch the Benchmark Dashboard **

```bash
cd /mnt/c/Users/HP/multicloud-ai-benchmark
python3 -m streamlit run dashboard/streamlit_app.py
```
Then open:

```
http://localhost:8501
```




=================================EXECUTION COMPLETED==========================================



Dashboard shows:

* Latency by provider
* Success / failure
* Response preview
* Summary JSON

---

### 🔥 Project Goal (Recap)

| Cloud        | Deployment            | Benchmarked |
| ------------ | --------------------- | ----------- |
| Azure OpenAI | Deployed GPT-35-Turbo | Yes         |
| AWS Bedrock  | Enabled model + IAM   | Yes         |

✔ Unified benchmark framework
✔ Results recorded
✔ Dashboard visualization

---

### 🎯 Key Files in the Repository

| File                                 | Purpose                                      |
| ------------------------------------ | -------------------------------------------- |
| `README.md`                          | Complete deployment + benchmark instructions |
| `requirements.txt`                   | Python dependencies                          |
| `config/providers.yaml`              | Cloud model configuration                    |
| `bench/bench.py`                     | Core benchmark script                        |
| `dashboard/streamlit_app.py`         | Visualization dashboard                      |
| `results/`                           | Output folder for CSV + JSON                 |
| `orchestrator/app.py` (optional)     | FastAPI benchmark endpoint                   |
| `iam/bedrock-policy.json` (optional) | AWS IAM policy JSON                          |

---

### 🚀 After pushing to GitHub

Anyone can run:

```
pip3 install -r requirements.txt
python3 -m bench.bench
python3 -m streamlit run dashboard/streamlit_app.py
```
--------------
### extra but usefull cmds

export AZURE_OPENAI_API_KEY="your_key"

export AWS_ACCESS_KEY_ID="your_key"

export AWS_SECRET_ACCESS_KEY="your_secret"

export AWS_DEFAULT_REGION="us-east-1"
