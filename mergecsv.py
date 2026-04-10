import pandas as pd
from pathlib import Path

base_path = Path("data/processed")

target_columns = [
    'satellite_name', 'owner_code', 'launch_date', 'decay_date', 
    'time_in_orbit_years', 'expected_lifetime_yrs', 'operator', 
    'country', 'mission_type', 'mission_end_date', 'compliance_deadline', 
    'age_years', 'orbit_class', 'operator_reliability_score', 
    'operator_compliance_rate', 'ml_risk_score', 'final_risk_tier'
]

def merge_and_filter():
    base_path = Path("data/processed")

    master = pd.read_csv(base_path / "satellite_risk_scores.csv")
    labelled = pd.read_csv(base_path / "labeled_satellites.csv")

    # Merge on NORAD ID
    df = master.merge(labelled, on="norad_id", how="left")

    # Keep only columns that actually exist
    cols = [c for c in target_columns if c in df.columns]
    final_df = df[cols]

    # Save
    output_path = base_path / "filtered_satellite_risk_data.csv"
    final_df.to_csv(output_path, index=False)

    print(final_df.head())
    print(f"\nSaved to {output_path}")

    return final_df


if __name__ == "__main__":
    merge_and_filter()