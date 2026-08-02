import os
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

logger = logging.getLogger(__name__)

class MetricsCalculator:
    def evaluate(self, predictions_df: pd.DataFrame, true_label_col: str = "label", pred_col: str = "decision", output_dir: str = "data/output") -> dict:
        """
        Calculates performance metrics against ground-truth labels if they exist in the dataset.
        Generates and saves a confusion matrix visualization.
        """
        # Check if ground truth exists
        if true_label_col not in predictions_df.columns:
            logger.warning(f"Ground truth column '{true_label_col}' not found. Skipping evaluation calculations.")
            return {}

        # Standardize capitalization of comparisons
        y_true = predictions_df[true_label_col].fillna("").astype(str).str.strip().str.capitalize().tolist()
        y_pred = predictions_df[pred_col].fillna("").astype(str).str.strip().str.capitalize().tolist()

        # Handle empty arrays safely
        if not y_true or not y_pred:
            logger.warning("Empty records for evaluation. Skipping.")
            return {}

        # List unique classes
        labels = sorted(list(set(y_true + y_pred)))
        
        # Calculate metrics
        acc = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )

        logger.info("=== EVALUATION REPORT ===")
        logger.info(f"Accuracy:  {acc:.4f}")
        logger.info(f"Precision (Weighted): {precision:.4f}")
        logger.info(f"Recall (Weighted):    {recall:.4f}")
        logger.info(f"F1 Score (Weighted):  {f1:.4f}")
        logger.info("=========================")

        # Plot and save Confusion Matrix using matplotlib and seaborn if possible
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.figure(figsize=(6, 5))
            sns.heatmap(
                cm, 
                annot=True, 
                fmt="d", 
                xticklabels=labels, 
                yticklabels=labels, 
                cmap="Blues", 
                cbar=False
            )
            plt.title("Notification Router Confusion Matrix")
            plt.xlabel("Predicted Routing")
            plt.ylabel("Actual Label")
            plt.tight_layout()

            os.makedirs(output_dir, exist_ok=True)
            plot_path = os.path.join(output_dir, "confusion_matrix.png")
            plt.savefig(plot_path, dpi=150)
            plt.close()
            logger.info(f"Confusion matrix plot successfully saved to {plot_path}")
        except Exception as e:
            logger.warning(f"Could not render/save confusion matrix plot: {e}. Outputting raw array instead.")
            logger.info(f"Confusion Matrix Array:\n{cm}")
            logger.info(f"Classes: {labels}")

        return {
            "accuracy": acc,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": cm.tolist(),
            "labels": labels
        }
