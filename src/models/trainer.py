import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from src.features.pipeline import build_preprocessor, NUMERIC_FEATURES, CATEGORICAL_FEATURES


def train_risk_model(df: pd.DataFrame, target_col: str = "is_compliant") -> Pipeline:

    """
    Trains a machine learning model to predict satellite compliance risk.

    This function:
    1. Selects relevant features and splits data into training/testing sets.
    2. Combines preprocessing and a Gradient Boosting classifier into a pipeline.
    3. Fits the model and calculates a cross-validation score to measure accuracy.

    Args:
        df: The dataset containing satellite features and the target label.
        target_col: The name of the column we are trying to predict.

    Returns:
        Pipeline: A fully trained and validated machine learning model.
    """

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    available = [c for c in feature_cols if c in df.columns]

    X = df[available]
    y = df[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("classifier", GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ])

    model.fit(X_train, y_train)
    cv_auc = cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc").mean()
    print(f"[Trainer] CV AUC: {cv_auc:.3f}")
    return model