import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parent

VARIANTS = {
    "full": {"suffix": "", "title": "Without Feature Reduction", "file": "roc_without_feature_reduction.png"},
    "anova": {"suffix": "_anova", "title": "ANOVA", "file": "roc_anova.png"},
    "fi": {"suffix": "_fi", "title": "Feature Importance", "file": "roc_feature_importance.png"},
    "lcc": {"suffix": "_lcc", "title": "Linear Correlation Coefficient", "file": "roc_lcc.png"},
    "pca": {"suffix": "_pca", "title": "PCA", "file": "roc_pca.png"},
}

MODELS = [
    ("DT", "Decision Tree", "green"),
    ("RF", "Random Forest", "red"),
    ("KNN", "KNN", "brown"),
    ("LR", "Logistic Regression", "orange"),
    ("SVM", "SVM", "blue"),
    ("resnet18", "ResNet-18", "black"),
    ("googlenet", "GoogLeNet", "purple"),
]


def artifact_name(model_key, suffix):
    if model_key in {"resnet18", "googlenet"}:
        return f"{model_key}_part_detrend_plr_stft_bin_win{suffix}.npz"
    return f"{model_key}{suffix}.npz"


def load_roc(model_key, suffix):
    path = PROJECT_DIR / "result" / "roc_artifacts" / artifact_name(model_key, suffix)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing ROC artifact: {path}")
    data = np.load(path)
    return data["fpr"], data["tpr"], float(data["roc_auc"])


def save_variant_figure(variant, meta):
    suffix = meta["suffix"]
    plt.figure(figsize=(7, 7))
    for model_key, label, color in MODELS:
        fpr, tpr, roc_auc = load_roc(model_key, suffix)
        plt.plot(fpr, tpr, label=f"{label} ROC curve (area = {roc_auc:0.2f})", color=color)

    plt.plot([0, 1], [0, 1], "k--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC ({meta['title']})")
    plt.legend(loc="lower right")
    plt.tight_layout()

    out_path = PROJECT_DIR / "result" / meta["file"]
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {out_path}")


def main():
    (PROJECT_DIR / "result").mkdir(exist_ok=True)
    for variant, meta in VARIANTS.items():
        save_variant_figure(variant, meta)


if __name__ == "__main__":
    main()
