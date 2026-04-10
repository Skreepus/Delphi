"""
Model evaluation and SHAP explainability.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import Pipeline


def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Print and return key classification metrics."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)
    print(f"[Evaluator] AUC: {auc:.3f}")
    print(classification_report(y_test, y_pred))
    return {"auc": auc, "report": report}


def get_shap_values(model: Pipeline, X: pd.DataFrame):
    """
    Return SHAP values for feature importance visualisation.
    Requires the `shap` package.
    """
    import shap
    classifier = model.named_steps["classifier"]
    X_transformed = model.named_steps["preprocessor"].transform(X)
    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(X_transformed)
    return shap_values, explainer
