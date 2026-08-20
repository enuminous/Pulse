import numpy as np
import pandas as pd

EPS = 1e-8

def robust_z(s, window=23):
    s = s.astype(float)
    med = s.rolling(window, min_periods=3).median()
    mad = (s-med).abs().rolling(window, min_periods=3).median()
    return ((s-med)/(1.4826*mad+EPS)).replace([np.inf,-np.inf], np.nan).fillna(0.0)

def build_pulse_features(df, feature_columns, horizons=(3,7,23)):
    x = df[feature_columns].astype(float).copy()
    out = pd.DataFrame(index=df.index)

    for c in feature_columns:
        out[f"{c}__z"] = robust_z(x[c], max(horizons))
        out[f"{c}__dx"] = x[c].diff().fillna(0.0)

    def get(name):
        return x[name] if name in x.columns else pd.Series(0.0, index=x.index)

    uncertainty = (
        (1.0 - get("model_confidence").clip(0,1))
        + get("entropy").rank(pct=True)
    ) / 2.0

    reviewer_instability = (
        get("reviewer_disagreement").clip(0,1)
        + get("correction_magnitude").rank(pct=True)
        + get("escalation").clip(0,1)
    ) / 3.0

    safety_pressure = (
        get("critical_miss").clip(0,1)
        + get("unsafe_output").clip(0,1)
        + get("abstention").clip(0,1)
        + get("repeated_failure").clip(0,1)
    ) / 4.0

    distribution_pressure = (
        get("model_version_shift").clip(0,1)
        + get("distribution_shift_score").rank(pct=True)
    ) / 2.0

    out["uncertainty_state"] = uncertainty
    out["reviewer_instability"] = reviewer_instability
    out["safety_pressure"] = safety_pressure
    out["distribution_pressure"] = distribution_pressure

    out["longitudinal_contradiction"] = (
        uncertainty.rank(pct=True)
        + reviewer_instability.rank(pct=True)
        + safety_pressure.rank(pct=True)
        + distribution_pressure.rank(pct=True)
    ) / 4.0

    out["safety_velocity"] = out["longitudinal_contradiction"].diff().fillna(0.0)
    out["safety_acceleration"] = out["safety_velocity"].diff().fillna(0.0)

    for h in horizons:
        out[f"uncertainty_mean_{h}"] = out["uncertainty_state"].rolling(h, min_periods=1).mean()
        out[f"reviewer_mean_{h}"] = out["reviewer_instability"].rolling(h, min_periods=1).mean()
        out[f"safety_mean_{h}"] = out["safety_pressure"].rolling(h, min_periods=1).mean()
        out[f"distribution_mean_{h}"] = out["distribution_pressure"].rolling(h, min_periods=1).mean()
        out[f"contradiction_mean_{h}"] = out["longitudinal_contradiction"].rolling(h, min_periods=1).mean()

    components = [
        out["uncertainty_state"],
        out["reviewer_instability"],
        out["safety_pressure"],
        out["distribution_pressure"],
        out["longitudinal_contradiction"],
        out["safety_velocity"].clip(lower=0),
        out["safety_acceleration"].clip(lower=0),
    ]
    for h in horizons:
        components.extend([
            out[f"uncertainty_mean_{h}"],
            out[f"reviewer_mean_{h}"],
            out[f"safety_mean_{h}"],
            out[f"distribution_mean_{h}"],
            out[f"contradiction_mean_{h}"],
        ])

    ranked = pd.concat(components, axis=1).rank(pct=True)
    out["pulse_risk_score"] = ranked.mean(axis=1).fillna(0.0)

    return out.replace([np.inf,-np.inf], np.nan).fillna(0.0)
