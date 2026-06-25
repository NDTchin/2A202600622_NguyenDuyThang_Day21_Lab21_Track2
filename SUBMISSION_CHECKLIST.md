# Submission Checklist

## Screenshots to capture
- MLflow UI showing at least 3 runs with different hyperparameters.
- GitHub Actions run showing `Unit Test`, `Train`, `Eval`, and `Deploy` all green.
- Cloud Storage showing DVC-tracked data objects and `models/latest/model.pkl`.
- `curl http://<VM_IP>:8000/health` output.
- `curl -X POST http://<VM_IP>:8000/predict ...` output.
- Step 3 Actions run triggered by the data commit message.

## Short report outline
- Best hyperparameters or best `model_type` and why you selected them.
- Best observed `accuracy` and `f1_score` from MLflow.
- Whether Step 3 improved the model after adding data.
- Any issue faced with DVC, GitHub Actions, or VM deployment and how you solved it.

## Current local benchmark
- Best local result found so far: RandomForest with `n_estimators=300`, `max_depth=None`, `min_samples_split=2`.
- Observed local metrics: `accuracy ~= 0.682`, `f1_score ~= 0.681`.
- This means the repo is technically ready, but the `0.70` eval gate may still require more tuning or benefit from the expanded Step 3 dataset.

## Bonus evidence
- Bonus 2: show MLflow runs from at least 2 model types.
- Bonus 3: show `outputs/report.txt` in GitHub Actions artifact.
- Bonus 4: mention rollback protection in workflow logs.
- Bonus 5: mention label distribution stored in `outputs/metrics.json` and warning log behavior.
