# Runbook

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

Suggested combinations:
```yaml
model_type: random_forest
n_estimators: 50
max_depth: 3
min_samples_split: 2
```

```yaml
model_type: random_forest
n_estimators: 100
max_depth: 5
min_samples_split: 2
```

```yaml
model_type: gradient_boosting
n_estimators: 150
learning_rate: 0.1
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

Note:
- The CI eval gate is still `0.70` as required by the lab.
- With the current local benchmark, the codebase is ready, but the pipeline may still stop at `Eval` until a stronger configuration or better training data setup is found.

## 3. DVC and GCP setup
```powershell
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
$env:PROJECT="<YOUR_PROJECT_ID>"
$env:BUCKET="<YOUR_UNIQUE_BUCKET_NAME>"
gcloud services enable storage.googleapis.com --project $env:PROJECT
gsutil mb -p $env:PROJECT -l us-central1 gs://$env:BUCKET
gcloud iam service-accounts create mlops-lab-sa --display-name "MLOps Lab SA" --project $env:PROJECT
gsutil iam ch serviceAccount:mlops-lab-sa@$env:PROJECT.iam.gserviceaccount.com:roles/storage.objectAdmin gs://$env:BUCKET
gcloud iam service-accounts keys create sa-key.json --iam-account mlops-lab-sa@$env:PROJECT.iam.gserviceaccount.com
dvc init
dvc remote add -d myremote gs://$env:BUCKET/dvc
dvc remote modify myremote credentialpath sa-key.json
dvc add data/train_phase1.csv
dvc add data/eval.csv
dvc add data/train_phase2.csv
git add .dvc .gitignore data\train_phase1.csv.dvc data\eval.csv.dvc data\train_phase2.csv.dvc
git commit -m "feat: track datasets with DVC"
dvc push
```

## 4. VM setup
```powershell
gcloud compute instances create mlops-serve --zone=us-central1-a --machine-type=e2-small --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --tags=mlops-serve --project $env:PROJECT
gcloud compute firewall-rules create allow-mlops-serve --allow=tcp:8000 --target-tags=mlops-serve --project $env:PROJECT
gcloud compute instances describe mlops-serve --zone=us-central1-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

Inside VM:
```bash
sudo apt update && sudo apt install -y python3-pip
pip3 install fastapi uvicorn scikit-learn joblib google-cloud-storage
mkdir -p ~/models ~/src
```

Copy files:
```powershell
gcloud compute scp src/serve.py mlops-serve:~/src/serve.py --zone=us-central1-a
gcloud compute scp sa-key.json mlops-serve:~/sa-key.json --zone=us-central1-a
```

Create systemd service inside VM:
```bash
sudo tee /etc/systemd/system/mlops-serve.service > /dev/null <<EOF
[Unit]
Description=MLOps Model Inference Server
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER
Environment="GCS_BUCKET=<YOUR_BUCKET_NAME>"
Environment="GOOGLE_APPLICATION_CREDENTIALS=/home/$USER/sa-key.json"
ExecStart=/usr/bin/python3 /home/$USER/src/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
echo $USER
```

## 5. GitHub deploy key and secrets
```powershell
ssh-keygen -t ed25519 -f $HOME\.ssh\mlops_deploy -N "" -C "github-actions-deploy"
gcloud compute ssh mlops-serve --zone=us-central1-a --command "echo '$(Get-Content $HOME\.ssh\mlops_deploy.pub)' >> ~/.ssh/authorized_keys"
```

Create these secrets in GitHub:
- `CLOUD_CREDENTIALS`
- `CLOUD_BUCKET`
- `VM_HOST`
- `VM_USER`
- `VM_SSH_KEY`

## 6. First pipeline run
```powershell
git add .
git commit -m "feat: complete mlops lab pipeline"
git push origin main
gcloud compute ssh mlops-serve --zone=us-central1-a --command "sudo systemctl start mlops-serve"
```

## 7. API checks
```powershell
$VM_IP="<YOUR_VM_IP>"
curl http://$VM_IP`:8000/health
curl -X POST http://$VM_IP`:8000/predict -H "Content-Type: application/json" -d '{"features":[7.4,0.70,0.00,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4,0]}'
```

## 8. Step 3 continuous training
```powershell
python add_new_data.py
dvc add data/train_phase1.csv
git add data/train_phase1.csv.dvc
git commit -m "data: bo sung 2998 mau du lieu moi"
dvc push
git push origin main
```
