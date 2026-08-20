from dataclasses import dataclass
import pandas as pd

from features import build_pulse_features
from baselines import LogisticModel, BaseRateModel, single_feature
from metrics import binary_metrics, stratify

@dataclass
class PULSEExperiment:
    time_column: str
    target_column: str
    feature_columns: list
    horizons: tuple = (3,7,23)
    train_fraction: float = 0.65
    random_state: int = 23

    def run(self, df):
        df = df.sort_values(self.time_column).reset_index(drop=True).copy()
        cut = max(20, int(len(df)*self.train_fraction))
        y = df[self.target_column].astype(int).to_numpy()

        pf = build_pulse_features(df, self.feature_columns, self.horizons)
        raw = df[self.feature_columns].astype(float).ffill().fillna(0.0)
        full = pd.concat([raw, pf], axis=1).fillna(0.0)

        uncertainty = single_feature(df, "entropy")
        disagreement = single_feature(df, "reviewer_disagreement")
        correction = single_feature(df, "correction_magnitude")

        models = {
            "pulse": (LogisticModel(self.random_state), full),
            "raw_evaluation": (LogisticModel(self.random_state), raw),
            "uncertainty_only": (LogisticModel(self.random_state), uncertainty),
            "disagreement_only": (LogisticModel(self.random_state), disagreement),
            "correction_only": (LogisticModel(self.random_state), correction),
            "base_rate": (BaseRateModel(), raw),
        }

        results = {}
        for name, (model, X) in models.items():
            model.fit(X.iloc[:cut], y[:cut])
            p = model.predict_proba(X.iloc[cut:])
            results[name] = {
                "overall": binary_metrics(y[cut:], p),
                "by_reviewer_disagreement": stratify(
                    y[cut:], p,
                    df["reviewer_disagreement"].to_numpy()[cut:]
                    if "reviewer_disagreement" in df.columns
                    else [0.0]*(len(df)-cut),
                    "low_disagreement",
                    "high_disagreement"
                ),
                "by_uncertainty": stratify(
                    y[cut:], p,
                    pf["uncertainty_state"].to_numpy()[cut:],
                    "low_uncertainty",
                    "high_uncertainty"
                )
            }

        return {
            "n_total": len(df),
            "train_n": cut,
            "test_n": len(df)-cut,
            "results": results,
            "primary_delta_brier_raw_minus_pulse": (
                results["raw_evaluation"]["overall"]["brier"]
                - results["pulse"]["overall"]["brier"]
            ),
            "interpretation": (
                "Positive delta favors PULSE over the matched raw-evaluation model. "
                "PULSE evaluates AI-system reliability, not patient state."
            )
        }
