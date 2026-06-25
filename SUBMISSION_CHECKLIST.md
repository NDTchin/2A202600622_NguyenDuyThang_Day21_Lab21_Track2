# Submission Checklist

## Infra completed
- DVC remote configured to GCS bucket `clean-evening-499803-c3-day21-track2-2a202600622`
- DVC datasets pushed successfully
- VM `mlops-serve` running at `34.133.45.220`
- Public `/health` endpoint working
- Public `/predict` endpoint working
- GitHub Actions GCP auth migrated to Workload Identity Federation

## Screenshots to capture
- MLflow UI showing at least 3 runs with different hyperparameters.
- GitHub Actions run showing `Unit Test`, `Train`, `Eval`, and `Deploy` all green.
- Cloud Storage showing DVC-tracked data objects and `models/latest/model.pkl`.
- `curl http://34.133.45.220:8000/health` output.
- Prediction output from `POST /predict`.
- Step 3 Actions run triggered by the data commit message.

## Manual actions still needed
- Add GitHub secrets: `VM_HOST`, `VM_USER`, `VM_SSH_KEY`.
- Push the current infra changes to GitHub.
- Trigger GitHub Actions.

## Current local benchmark
- Best local result found so far: RandomForest with `n_estimators=300`, `max_depth=None`, `min_samples_split=2`.
- Observed local metrics: `accuracy ~= 0.682`, `f1_score ~= 0.681`.
- This means the infra is ready, but the `0.70` eval gate may still stop deployment until a stronger model configuration is found or the larger Step 3 dataset helps.

## Bonus evidence
- Bonus 2: show MLflow runs from at least 2 model types.
- Bonus 3: show `outputs/report.txt` in GitHub Actions artifact.
- Bonus 4: mention rollback protection in workflow logs.
- Bonus 5: mention label distribution stored in `outputs/metrics.json` and warning log behavior.
