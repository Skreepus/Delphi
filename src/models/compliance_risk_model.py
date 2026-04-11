"""
Compliance Risk Model (Simplified — Logistic Regression)

Math used:
    1. Z-score normalisation:  z = (x - μ) / σ
    2. Logistic regression:    P(compliant) = 1 / (1 + e^(-z))
       where z = b₀ + b₁x₁ + b₂x₂ + ...
    3. Risk score:             risk = 1 - P(compliant)

No complex pipelines. No gradient boosting. No SHAP.
Every step is visible and uses intro-stats-level math.

The model learns ONE weight per feature. That's it.
Positive weight = feature pushes toward compliance.
Negative weight = feature pushes toward non-compliance (risk).
"""

import pandas as pd
import numpy as np
import os
import json

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from config import (
    FEATURE_TABLE_CSV,
    SATELLITE_RISK_CSV,
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
)
from src.features.feature_engineering import NUMERIC_FEATURES

# ── Paths ───────────────────────────────────────────────────────
MODEL_DIR = os.path.join("data", "models")
COEFFICIENTS_PATH = os.path.join(MODEL_DIR, "model_coefficients.csv")
EVAL_PATH = os.path.join(MODEL_DIR, "model_evaluation.json")
NORMALISATION_PATH = os.path.join(MODEL_DIR, "normalisation_params.csv")


# ════════════════════════════════════════════════════════════════
# Step 1: Z-Score Normalisation (manual — no sklearn)
# ════════════════════════════════════════════════════════════════


def compute_normalisation_params(train_df: pd.DataFrame, features: list) -> pd.DataFrame:
    """
    Compute mean and standard deviation for each feature from training data.

    These are saved so we can apply the same normalisation to new data.

    Formula: z = (x - mean) / std
    """
    params = []
    for feat in features:
        if feat in train_df.columns:
            mean = train_df[feat].mean()
            std = train_df[feat].std()
            # Prevent division by zero
            if std == 0:
                std = 1.0
            params.append({"feature": feat, "mean": mean, "std": std})

    return pd.DataFrame(params)


def normalise(df: pd.DataFrame, params: pd.DataFrame) -> pd.DataFrame:
    """
    Apply z-score normalisation using pre-computed mean and std.

    For each feature:  z = (x - mean) / std

    This puts all features on the same scale so that
    'altitude in km' doesn't dominate 'age in years'.
    """
    df = df.copy()
    for _, row in params.iterrows():
        feat = row["feature"]
        if feat in df.columns:
            df[feat] = (df[feat] - row["mean"]) / row["std"]
    return df


# ════════════════════════════════════════════════════════════════
# Step 2: Prepare Data
# ════════════════════════════════════════════════════════════════


def prepare_data(df: pd.DataFrame):
    # No orbit dummies anymore — just use NUMERIC_FEATURES directly
    feature_cols = [c for c in NUMERIC_FEATURES if c in df.columns]

    train_mask = df["compliance_label"].isin(["compliant", "non_compliant"])
    predict_mask = df["compliance_label"] == "unknown"

    train_df = df[train_mask].copy()
    predict_df = df[predict_mask].copy()

    X_train = train_df[feature_cols]
    y_train = train_df["is_compliant"].astype(int)
    X_predict = predict_df[feature_cols]

    return X_train, y_train, X_predict, feature_cols, train_df, predict_df


# ════════════════════════════════════════════════════════════════
# Step 3: Train Logistic Regression
# ════════════════════════════════════════════════════════════════


def train_model(feature_table_path=FEATURE_TABLE_CSV) -> dict:
    """
    Train a logistic regression model and predict risk for active satellites.

    The model learns:
        P(compliant) = 1 / (1 + e^(-(b₀ + b₁x₁ + b₂x₂ + ...)))

    Where b₀ is the intercept and b₁, b₂, ... are weights (one per feature).
    Positive weight = feature helps compliance.
    Negative weight = feature hurts compliance (increases risk).

    Steps:
        1. Load feature table
        2. Split into train (80%) and test (20%)
        3. Compute z-score normalisation from training data
        4. Normalise both train and test
        5. Train logistic regression
        6. Evaluate on test set
        7. Print model coefficients (the explanation)
        8. Predict on active satellites
        9. Save everything
    """
    print("=" * 60)
    print("TRAINING COMPLIANCE RISK MODEL")
    print("Logistic Regression (simplified)")
    print("=" * 60)

    # ── Load ────────────────────────────────────────────────────
    print(f"\nLoading: {feature_table_path}")
    df = pd.read_csv(feature_table_path, low_memory=False)
    print(f"  Total rows: {len(df):,}")

    # ── Prepare data ────────────────────────────────────────────
    X_full, y_full, X_predict, feature_cols, train_df, predict_df = prepare_data(df)
    print(f"  Training rows:    {len(X_full):,}")
    print(f"  Prediction rows:  {len(X_predict):,}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Class balance: {y_full.sum():,} compliant, {(1-y_full).sum().astype(int):,} non-compliant")

    # ── Split into train / test ─────────────────────────────────
    print(f"\n── Step 1: Train/Test Split (80/20) ──")
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, y_full,
        test_size=0.2,
        random_state=67,
        stratify=y_full,
    )
    print(f"  Train: {len(X_train):,}")
    print(f"  Test:  {len(X_test):,}")

    # ── Normalise ───────────────────────────────────────────────
    print(f"\n── Step 2: Z-Score Normalisation ──")
    print(f"  Formula: z = (x - mean) / std")
    norm_params = compute_normalisation_params(X_train, feature_cols)

    X_train_norm = normalise(X_train, norm_params)
    X_test_norm = normalise(X_test, norm_params)

    print(f"  Computed mean and std for {len(norm_params)} features")

    # ── Train logistic regression ───────────────────────────────
    print(f"\n── Step 3: Train Logistic Regression ──")
    print(f"  P(compliant) = 1 / (1 + e^(-(b₀ + b₁x₁ + b₂x₂ + ...)))")

    model = LogisticRegression(
        max_iter=1000,
        random_state=67,
    )
    model.fit(X_train_norm, y_train)
    print(f"  Model trained ✅")

    # ── Evaluate on test set ────────────────────────────────────
    print(f"\n── Step 4: Evaluate on Test Set ──")

    y_pred = model.predict(X_test_norm)
    y_prob = model.predict_proba(X_test_norm)[:, 1]  # P(compliant)

    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    print(f"  Accuracy: {accuracy:.3f}  ({accuracy*100:.1f}% correct)")
    print(f"  AUC:      {auc:.3f}")
    print(f"\n  Confusion Matrix:")
    print(f"                   Predicted")
    print(f"                Non-comp  Compliant")
    print(f"  Actual NC      {cm[0][0]:>5}     {cm[0][1]:>5}")
    print(f"  Actual C       {cm[1][0]:>5}     {cm[1][1]:>5}")
    print()
    print(classification_report(
        y_test, y_pred,
        target_names=["non_compliant", "compliant"]
    ))

    # ── Show model coefficients ─────────────────────────────────
    print(f"── Step 5: Model Coefficients (What the Model Learned) ──")
    print(f"  Each coefficient = how much that feature affects compliance")
    print(f"  Positive = pushes toward compliant (lower risk)")
    print(f"  Negative = pushes toward non-compliant (higher risk)")
    print()

    intercept = float(model.intercept_[0])
    coefficients = model.coef_[0]

    coef_df = pd.DataFrame({
        "feature": feature_cols,
        "coefficient": coefficients,
        "abs_coefficient": np.abs(coefficients),
        "direction": ["→ compliance" if c > 0 else "→ risk" for c in coefficients],
    }).sort_values("abs_coefficient", ascending=False)

    print(f"  Intercept (b₀): {intercept:.4f}")
    print()
    for _, row in coef_df.iterrows():
        bar_len = int(row["abs_coefficient"] * 10)
        bar = "█" * min(bar_len, 30)
        sign = "+" if row["coefficient"] > 0 else "-"
        print(f"  {sign}{row['abs_coefficient']:.4f}  {row['feature']:35s}  {row['direction']}  {bar}")

    # ── Retrain on full training set for final predictions ──────
    print(f"\n── Step 6: Retrain on Full Training Set ──")
    norm_params_full = compute_normalisation_params(X_full, feature_cols)
    X_full_norm = normalise(X_full, norm_params_full)

    model.fit(X_full_norm, y_full)
    print(f"  Retrained on {len(X_full):,} rows")

    # Update coefficients after retraining
    intercept = float(model.intercept_[0])
    coefficients = model.coef_[0]
    coef_df = pd.DataFrame({
        "feature": feature_cols,
        "coefficient": [float(c) for c in coefficients],
    })

    # ── Predict on active satellites ────────────────────────────
    print(f"\n── Step 7: Predict on Active Satellites ──")

    if len(X_predict) > 0:
        X_predict_norm = normalise(X_predict, norm_params_full)

        # P(compliant) for each active satellite
        prob_compliant = model.predict_proba(X_predict_norm)[:, 1]

        # Risk = 1 - P(compliant) = P(non_compliant)
        predict_df = predict_df.copy()
        predict_df["ml_compliance_probability"] = prob_compliant
        predict_df["ml_risk_score"] = 1 - prob_compliant

        # Also score training data
        train_prob = model.predict_proba(X_full_norm)[:, 1]
        train_df = train_df.copy()
        train_df["ml_compliance_probability"] = train_prob
        train_df["ml_risk_score"] = 1 - train_prob
    else:
        predict_df["ml_compliance_probability"] = np.nan
        predict_df["ml_risk_score"] = np.nan
        train_df["ml_compliance_probability"] = np.nan
        train_df["ml_risk_score"] = np.nan

    # ── Combine into full scored table ──────────────────────────
    other_df = df[
        ~df.index.isin(train_df.index) & ~df.index.isin(predict_df.index)
    ].copy()
    if len(other_df) > 0:
        other_df["ml_compliance_probability"] = np.nan
        other_df["ml_risk_score"] = np.nan

    scored = pd.concat([train_df, predict_df, other_df], ignore_index=True)

    # ── Assign risk tiers ───────────────────────────────────────
    scored["final_risk_score"] = scored["ml_risk_score"].fillna(0.5)

    scored["final_risk_tier"] = np.where(
        scored["final_risk_score"] > RISK_HIGH_THRESHOLD, "HIGH",
        np.where(
            scored["final_risk_score"] > RISK_MEDIUM_THRESHOLD, "MEDIUM", "LOW"
        )
    )

    # ── Summary ─────────────────────────────────────────────────
    active = scored[scored["compliance_label"] == "unknown"]
    if len(active) > 0:
        tier_counts = active["final_risk_tier"].value_counts()
        print(f"\n── Active Satellite Risk Distribution ──")
        for tier in ["HIGH", "MEDIUM", "LOW"]:
            n = tier_counts.get(tier, 0)
            pct = n / len(active) * 100
            print(f"  {tier:8s}  {n:>7,}  ({pct:5.1f}%)")

        # Top 10 highest risk
        worst = active.nlargest(10, "final_risk_score")
        display_cols = [
            "norad_id", "satellite_name", "operator_final",
            "orbit_class", "age_years", "operator_reliability_score",
            "ml_risk_score", "final_risk_tier",
        ]
        display_cols = [c for c in display_cols if c in worst.columns]
        print(f"\n── 10 Highest Risk Active Satellites ──")
        print(worst[display_cols].to_string(index=False))

    # ── Save ────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save coefficients (human-readable)
    coef_with_intercept = pd.concat([
        pd.DataFrame([{"feature": "intercept", "coefficient": intercept}]),
        coef_df,
    ], ignore_index=True)
    coef_with_intercept.to_csv(COEFFICIENTS_PATH, index=False)
    print(f"\n✅ Coefficients saved to {COEFFICIENTS_PATH}")

    # Save normalisation parameters
    norm_params_full.to_csv(NORMALISATION_PATH, index=False)
    print(f"✅ Normalisation params saved to {NORMALISATION_PATH}")

    # Save evaluation metrics
    eval_metrics = {
        "accuracy": float(accuracy),
        "auc": float(auc),
        "training_rows": int(len(X_full)),
        "prediction_rows": int(len(X_predict)),
        "features_used": feature_cols,
        "intercept": float(intercept),
        "confusion_matrix": {
            "true_negative": int(cm[0][0]),
            "false_positive": int(cm[0][1]),
            "false_negative": int(cm[1][0]),
            "true_positive": int(cm[1][1]),
        },
    }
    with open(EVAL_PATH, "w") as f:
        json.dump(eval_metrics, f, indent=2)
    print(f"✅ Evaluation saved to {EVAL_PATH}")

    # Save scored satellites
    scored.to_csv(SATELLITE_RISK_CSV, index=False)
    print(f"✅ Scored satellites saved to {SATELLITE_RISK_CSV}")
    print(f"   {len(scored):,} rows")

    try:
        from utils.satellite_risk_merge import export_enriched_satellite_risk_csv

        enriched_path = export_enriched_satellite_risk_csv()
        if enriched_path is not None:
            print(f"✅ Enriched export saved to {enriched_path}")
    except Exception as exc:
        print(f"⚠️ Could not write satellite_risk_enriched.csv: {exc}")

    return {
        "accuracy": accuracy,
        "auc": auc,
        "coefficients": coef_with_intercept,
        "scored_df": scored,
    }


if __name__ == "__main__":
    train_model()