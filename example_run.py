import json
import pandas as pd
from pulse import PULSEExperiment

df = pd.read_csv("example_data.csv")

features = [
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

exp = PULSEExperiment(
    time_column="case_index",
    target_column="future_clinical_failure",
    feature_columns=features,
    horizons=(3,7,23),
    random_state=23,
)

result = exp.run(df)
print(json.dumps(result, indent=2))
