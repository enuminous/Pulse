# PULSE

**Predictive Uncertainty and Longitudinal Safety Evaluation**

PULSE is an EFMW-derived framework for medical-AI reliability evaluation.

It is **not** a diagnostic system.

Its narrow question is:

> Can longitudinal patterns in model uncertainty, clinician disagreement, corrections, abstentions, and prior failures predict a later clinically meaningful AI failure better than standard evaluation signals alone?

## Intended uses

- retrospective medical-AI evaluation
- clinician-in-the-loop model monitoring
- benchmark auditing
- longitudinal safety analysis
- reviewer disagreement analysis
- escalation-risk prediction
- model-version comparison
- post-deployment evaluation research

## Core signal path

```text
model output
→ uncertainty
→ clinician review
→ disagreement
→ correction magnitude
→ abstention / escalation
→ repeated failure pattern
→ longitudinal safety state
→ PULSE risk score
```

## Ethical boundary

PULSE evaluates the **AI system**, not the patient.

It must not be used to:

- diagnose patients
- recommend treatment
- replace clinician judgment
- determine medical eligibility
- make autonomous clinical decisions

Clinician-reviewed labels remain the ground truth for evaluation.

## Flat-stack repository

```text
README.md
LICENSE
CITATION.cff
pyproject.toml
requirements.txt
pulse.py
features.py
baselines.py
metrics.py
freeze.py
safety_schema.json
example_config.yaml
example_data.csv
example_run.py
test_pulse.py
MANIFEST.sha256
```

## Scientific hypothesis

> In medical-AI evaluation workflows, clinically meaningful failures may be preceded by increasing uncertainty, reviewer disagreement, correction burden, recurrence, and escalation pressure.

PULSE does not assume that this hypothesis is true.

## Example features

- model_confidence
- entropy
- reviewer_disagreement
- correction_magnitude
- escalation
- abstention
- critical_miss
- unsafe_output
- repeated_failure
- reviewer_count
- model_version_shift
- distribution_shift_score

## Baselines

Included:

- raw evaluation-feature logistic model
- uncertainty-only baseline
- reviewer-disagreement baseline
- correction-only baseline
- base-rate predictor

## Primary endpoint

On a frozen retrospective or prospective dataset:

> Does PULSE improve prediction of subsequent clinically meaningful AI failure over the matched raw evaluation-feature model?

Primary metric:

- Brier score

Secondary metrics:

- log loss
- ROC-AUC
- average precision
- calibration
- performance stratified by reviewer disagreement
- performance stratified by model uncertainty

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python example_run.py
```

## Tests

```bash
pytest -q
```

## Minimal use

```python
import pandas as pd
from pulse import PULSEExperiment

df = pd.read_csv("example_data.csv")

exp = PULSEExperiment(
    time_column="case_index",
    target_column="future_clinical_failure",
    feature_columns=[
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
    ],
    horizons=(3, 7, 23),
)

print(exp.run(df))
```

## Freeze discipline

Before testing, freeze:

- target failure definition
- clinician-review label rules
- data inclusion/exclusion criteria
- de-identification requirements
- feature definitions
- horizons
- reviewer aggregation rule
- uncertainty metric
- baselines
- primary metric
- cutoff
- random seeds
- analysis procedure

Then run:

```bash
python freeze.py
```

## Recommended pilot design

1. Pick one medical-AI task.
2. Pick one clinically meaningful failure definition.
3. Use one frozen dataset.
4. Hide final clinician labels until model outputs are generated.
5. Compare PULSE against Senebiclabs/current evaluation baselines and matched non-PULSE controls.
6. Report every miss, false alarm, abstention, and exclusion.

## Negative results

If conventional evaluation features perform equally well, PULSE has not demonstrated incremental value.

## Status

Research software. Experimental. Not validated for clinical decision-making.
