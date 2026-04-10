"""
Model training for satellite disposal risk classification.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from src.features.pipeline import build_preprocessor, NUMERIC_FEATURES, CATEGORICAL_FEATURES


def train_risk_model(df: pd.DataFrame, target_col: str = "is_compliant") -> Pipeline:
    """
    Train a gradient boosting classifier on labelled historical data.

    Args:
        df: Feature-engineered DataFrame with compliance labels.
        target_col: Binary target column name.

    Returns:
        Fitted sklearn Pipeline (preprocessor + classifier).
    """
    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    available = [c for c in feature_cols if c in df.columns]

    X = df[available]
    y = df[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor()
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ])

    model.fit(X_train, y_train)
    print(f"[Trainer] CV AUC: {cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc').mean():.3f}")
    return model
