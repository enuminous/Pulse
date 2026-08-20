import pandas as pd
from features import build_pulse_features
from pulse import PULSEExperiment

FEATURES = [
    "model_confidence",
    "entropy",
    "reviewer_disagreement",
    "correction_magnitude",
    "escalation",
    "abstention",
    "critical_miss",
    "unsafe_output",
    "repeated_failure",
    "reviewer_count",
    "model_version_shift",
    "distribution_shift_score",
]

def test_features():
    df = pd.read_csv("example_data.csv")
    pf = build_pulse_features(df, FEATURES)
    assert len(pf) == len(df)
    assert "pulse_risk_score" in pf.columns
    assert pf["pulse_risk_score"].between(0,1).all()

def test_experiment_runs():
    df = pd.read_csv("example_data.csv")
    exp = PULSEExperiment(
        time_column="case_index",
        target_column="future_clinical_failure",
        feature_columns=FEATURES,
    )
    out = exp.run(df)
    assert "results" in out
    assert "pulse" in out["results"]
    assert "raw_evaluation" in out["results"]
