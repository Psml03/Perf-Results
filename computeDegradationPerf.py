import pandas as pd

def main():
   # Define paths for baseline and current (to be compared to) configurations
    baseline_file = "/path/to/ouput/folder/output_baseline.xlsx"
    current_file = "/path/to/ouput/folder/output_current.xlsx"
    output_file   = "/path/to/output/folder/output.xlsx"
    
    # Read the baseline and current Excel files into DataFrames
    baseline_df = pd.read_excel(baseline_file)
    current_df  = pd.read_excel(current_file)
    
    # Remove any rows with an empty 'perf metric'
    baseline_df = baseline_df[baseline_df["perf metric"].astype(str).str.strip() != ""]
    current_df  = current_df[current_df["perf metric"].astype(str).str.strip() != ""]

    # Merge both data sets
    merged_df = pd.merge(
        baseline_df[["perf metric", "Average"]],
        current_df[["perf metric", "Average"]],
        on="perf metric",
        suffixes=("_baseline", "_current")
    )

    # No need to calculate for these metrics
    skip_degradation = {"cpu-cycles", "instructions", "branch-instructions", "branch-misses"}

    # Compute degradation percentage
    def compute_degradation(row):
        metric = row["perf metric"]
        baseline_val = row["Average_baseline"]
        current_val  = row["Average_current"]
        if metric in skip_degradation:
            return None
        if baseline_val == 0:
            return None
        return ((baseline_val - current_val) / baseline_val) * 100

    # Degradation calculations for each row
    merged_df["Degradation (%)"] = merged_df.apply(compute_degradation, axis=1)

    # Reorder the columns.
    merged_df = merged_df[["perf metric", "Average_baseline", "Average_current", "Degradation (%)"]]

    # Save the result to a new Excel file
    merged_df.to_excel(output_file, index=False)
    print(f"Degradation report saved to {output_file}")

if __name__ == "__main__":
    main()
