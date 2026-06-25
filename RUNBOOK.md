# Runbook

## Current infra status
- GCP project: `clean-evening-499803-c3`
- GCS bucket: `clean-evening-499803-c3-day21-track2-2a202600622`
- VM public IP: `34.133.45.220`
- VM user: `Admin`
- GitHub Actions GCP auth: Workload Identity Federation configured
- Local DVC push: completed successfully
- VM `/health`: working
- VM `/predict`: working

## 1. Local setup
```powershell
cd D:\Vin\Lab\Day21-Track2-CI-CD-for-AI-Systems
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_data.py
$env:MLFLOW_TRACKING_URI="sqlite:///mlflow.db"
$env:MLFLOW_ARTIFACT_ROOT="./mlartifacts"
pytest tests\ -v
```

## 2. MLflow experiments
Run at least 3 experiments after editing `params.yaml` each time.
```powershell
python src/train.py
python src/train.py
python src/train.py
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Best local configuration found so far:
```yaml
model_type: random_forest
n_estimators: 300
max_depth:
min_samples_split: 2
```

Observed local result on `data/eval.csv`:
- `accuracy`: about `0.682`
- `f1_score`: about `0.681`

## 3. DVC setup on this project
This GCP project blocks service-account key creation, so local DVC uses your logged-in `gcloud` / ADC credentials instead of `sa-key.json`.

Already completed:
```powershell
.\.venv\Scripts\dvc.exe init
.\.venv\Scripts\dvc.exe remote add -d myremote gs://clean-evening-499803-c3-day21-track2-2a202600622/dvc
.\.venv\Scripts\dvc.exe add data\train_phase1.csv
.\.venv\Scripts\dvc.exe add data\eval.csv
.\.venv\Scripts\dvc.exe add data\train_phase2.csv
.\.venv\Scripts\dvc.exe push
```

## 4. VM serving setup
This VM uses the attached service account `mlops-lab-sa@clean-evening-499803-c3.iam.gserviceaccount.com`, so it does not need a copied key file.

Already completed:
- VM: `mlops-serve`
- Zone: `us-central1-a`
- Firewall rule `allow-mlops-serve`
- Uploaded `src/serve.py`
- Uploaded `models/latest/model.pkl`, `metrics.json`, `report.txt` to GCS
- Created and started `mlops-serve.service`

Verification:
```powershell
curl.exe http://34.133.45.220:8000/health
```

```powershell
$body = '{"features":[7.4,0.70,0.00,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4,0]}'
Invoke-RestMethod -Uri 'http://34.133.45.220:8000/predict' -Method Post -ContentType 'application/json' -Body $body | ConvertTo-Json -Compress
```

## 5. GitHub Actions auth
This project uses Workload Identity Federation instead of `CLOUD_CREDENTIALS`.

Already completed in GCP:
- Workload Identity Pool: `github-pool`
- Provider: `github-provider`
- Provider resource:
  `projects/650265798232/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- Bound repo:
  `NDTchin/2A202600622_NguyenDuyThang_Day21_Lab21_Track2`
- Service account:
  `mlops-lab-sa@clean-evening-499803-c3.iam.gserviceaccount.com`

## 6. Remaining GitHub secrets you still need to add manually
Add these repository secrets in GitHub:
- `VM_HOST` = `34.133.45.220`
- `VM_USER` = `Admin`
- `VM_SSH_KEY` = contents of `C:\Users\Admin\.ssh\mlops_deploy`

No `CLOUD_CREDENTIALS` secret is needed anymore.

## 7. Push infra code changes
```powershell
git add .github/workflows/mlops.yml .dvc .dvcignore data/*.dvc RUNBOOK.md SUBMISSION_CHECKLIST.md
git commit -m "infra: configure dvc, gcp bucket, vm, and keyless github auth"
git push origin main
```

## 8. Step 3 continuous training later
```powershell
python add_new_data.py
.\.venv\Scripts\dvc.exe add data\train_phase1.csv
git add data\train_phase1.csv.dvc
git commit -m "data: bo sung 2998 mau du lieu moi"
.\.venv\Scripts\dvc.exe push
git push origin main
```
