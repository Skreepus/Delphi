import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import Pipeline


def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Tests the model performance and prints accuracy metrics.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    print(f"[Evaluator] AUC: {auc:.3f}")
    print(classification_report(y_test, y_pred))
    return {"auc": auc}


def get_shap_values(model: Pipeline, X: pd.DataFrame):
    """
    Explains the model's predictions by identifying which features mattered most.
    """
    import shap
    classifier = model.named_steps["classifier"]
    X_transformed = model.named_steps["preprocessor"].transform(X)
    explainer = shap.TreeExplainer(classifier)
    return explainer.shap_values(X_transformed), explainer
