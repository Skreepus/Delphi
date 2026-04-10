"""
Model Evaluation (Simplified)

Just accuracy, AUC, and confusion matrix.
No SHAP. No cross-validation.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


def evaluate(y_true, y_pred, y_prob=None):
    """
    Print basic evaluation metrics.

    Parameters
    ----------
    y_true : array-like
        Actual labels (0 or 1)
    y_pred : array-like
        Predicted labels (0 or 1)
    y_prob : array-like, optional
        Predicted probabilities for the positive class

    Returns
    -------
    dict with accuracy, auc (if y_prob given)
    """
    acc = accuracy_score(y_true, y_pred)
    print(f"Accuracy: {acc:.3f}")

    cm = confusion_matrix(y_true, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"              Predicted")
    print(f"           Neg    Pos")
    print(f"  Act Neg  {cm[0][0]:>5}  {cm[0][1]:>5}")
    print(f"  Act Pos  {cm[1][0]:>5}  {cm[1][1]:>5}")

    print(classification_report(y_true, y_pred))

    results = {"accuracy": float(acc)}

    if y_prob is not None:
        auc = roc_auc_score(y_true, y_prob)
        print(f"AUC: {auc:.3f}")
        results["auc"] = float(auc)

    return results