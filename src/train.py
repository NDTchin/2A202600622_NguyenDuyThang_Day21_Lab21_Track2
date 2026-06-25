import json
import os

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

EVAL_THRESHOLD = 0.70
CLASS_LABELS = [0, 1, 2]
MODEL_TYPES = {
    "random_forest",
    "extra_trees",
    "gradient_boosting",
    "hist_gradient_boosting",
    "logistic_regression",
    "voting_rf_et",
}


def build_model(params: dict):
    model_type = params.get("model_type", "random_forest")

    if model_type not in MODEL_TYPES:
        raise ValueError(
            f"Unsupported model_type '{model_type}'. Choose one of: {sorted(MODEL_TYPES)}"
        )

    if model_type == "random_forest":
        return RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth"),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42,
            n_jobs=-1,
        )

    if model_type == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth"),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42,
            n_jobs=-1,
        )

    if model_type == "gradient_boosting":
        return GradientBoostingClassifier(
            n_estimators=params.get("n_estimators", 100),
            learning_rate=params.get("learning_rate", 0.1),
            random_state=42,
        )

    if model_type == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            max_depth=params.get("max_depth"),
            learning_rate=params.get("learning_rate", 0.1),
            max_iter=params.get("max_iter", 200),
            random_state=42,
        )

    if model_type == "voting_rf_et":
        rf = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 800),
            max_depth=params.get("max_depth"),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42,
            n_jobs=-1,
        )
        et = ExtraTreesClassifier(
            n_estimators=params.get("et_n_estimators", params.get("n_estimators", 800)),
            max_depth=params.get("et_max_depth", params.get("max_depth")),
            min_samples_split=params.get("et_min_samples_split", params.get("min_samples_split", 2)),
            random_state=42,
            n_jobs=-1,
        )
        return VotingClassifier(
            estimators=[("rf", rf), ("et", et)],
            voting=params.get("voting", "hard"),
        )

    return LogisticRegression(
        max_iter=params.get("max_iter", 1000),
        multi_class="auto",
        random_state=42,
    )


def load_training_data(data_path: str, params: dict) -> pd.DataFrame:
    df_train = pd.read_csv(data_path)
    include_phase2 = params.get("include_phase2_data", False)
    phase2_path = params.get("phase2_data_path", "data/train_phase2.csv")

    if include_phase2 and os.path.exists(phase2_path):
        df_phase2 = pd.read_csv(phase2_path)
        df_train = pd.concat([df_train, df_phase2], ignore_index=True)
        print(f"Merged additional training data from {phase2_path}: total rows = {len(df_train)}")

    return df_train


def make_distribution(y_train: pd.Series) -> dict:
    ratios = y_train.value_counts(normalize=True).sort_index()
    distribution = {
        str(label): float(ratios.get(label, 0.0))
        for label in CLASS_LABELS
    }
    return distribution


def write_report(path: str, acc: float, f1: float, distribution: dict, cm, precision, recall):
    lines = [
        f"accuracy: {acc:.4f}",
        f"f1_score: {f1:.4f}",
        "",
        "train_label_distribution:",
    ]

    for label in CLASS_LABELS:
        lines.append(f"  class_{label}: {distribution[str(label)]:.4f}")

    lines.extend([
        "",
        "confusion_matrix:",
    ])
    for row in cm:
        lines.append("  " + " ".join(str(int(value)) for value in row))

    lines.extend([
        "",
        "precision_recall_by_class:",
    ])
    for idx, label in enumerate(CLASS_LABELS):
        lines.append(
            f"  class_{label}: precision={precision[idx]:.4f}, recall={recall[idx]:.4f}"
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    df_train = load_training_data(data_path, params)
    df_eval = pd.read_csv(eval_path)

    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    distribution = make_distribution(y_train)
    for label, ratio in distribution.items():
        if ratio < 0.10:
            print(f"WARNING: class {label} chiem {ratio:.2%} < 10% du lieu huan luyen.")

    with mlflow.start_run():
        mlflow.log_params(params)

        model = build_model(params)
        model.fit(X_train, y_train)

        preds = model.predict(X_eval)
        acc = accuracy_score(y_eval, preds)
        f1 = f1_score(y_eval, preds, average="weighted")
        precision, recall, _, _ = precision_recall_fscore_support(
            y_eval,
            preds,
            labels=CLASS_LABELS,
            zero_division=0,
        )
        cm = confusion_matrix(y_eval, preds, labels=CLASS_LABELS)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        for label in CLASS_LABELS:
            mlflow.log_metric(
                f"train_label_ratio_{label}",
                distribution[str(label)],
            )
        mlflow.sklearn.log_model(model, "model")

        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")

        os.makedirs("outputs", exist_ok=True)
        metrics = {
            "accuracy": acc,
            "f1_score": f1,
            "eval_threshold": EVAL_THRESHOLD,
            "model_type": params.get("model_type", "random_forest"),
            "label_distribution": distribution,
            "precision_by_class": {
                str(label): float(precision[idx])
                for idx, label in enumerate(CLASS_LABELS)
            },
            "recall_by_class": {
                str(label): float(recall[idx])
                for idx, label in enumerate(CLASS_LABELS)
            },
            "confusion_matrix": cm.tolist(),
        }
        with open("outputs/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        write_report(
            "outputs/report.txt",
            acc,
            f1,
            distribution,
            cm,
            precision,
            recall,
        )

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

        mlflow.log_artifact("outputs/metrics.json")
        mlflow.log_artifact("outputs/report.txt")

    return float(acc)


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)
