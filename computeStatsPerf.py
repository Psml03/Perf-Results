import os
import glob
import re
import pandas as pd

# List of performance metrics in the desired order
DESIRED_METRICS = [
    "cpu-cycles",
    "instructions",
    "branch-instructions",
    "branch-misses",
    "cycle_activity.stalls_total",
    "misc2_retired.lfence"
]

#Only keep metrics from DESIRED_METRICS and remove headers and 'seconds time elapsed'
def parse_file(file_path):

    metrics = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            if line.startswith("Performance counter") or "seconds time elapsed" in line:
                continue

            tokens = re.split(r'\s+', line)
            if len(tokens) < 2:
                continue

            # Remove commas and convert to float
            value_str = tokens[0].replace(',', '')
            try:
                value = float(value_str)
            except ValueError:
                continue

            metric_name = tokens[1]
            # Only the desired metrics
            if metric_name in DESIRED_METRICS:
                metrics[metric_name] = value
    return metrics

def main():
    # Folders for input and output
    input_folder = "/path/to/input/folder"
    output_folder = "/path/to/output/folder"

    # Make sure output folder exists.
    os.makedirs(output_folder, exist_ok=True)

    # Find all .txt files in the input folder
    txt_files = sorted(glob.glob(os.path.join(input_folder, "*.txt")))
    
    if not txt_files:
        print("No .txt files found in the input folder.")
        return

    # Parse each file and collect metrics
    iterations = []
    for file in txt_files:
        file_metrics = parse_file(file)
        iterations.append(file_metrics)
        print(f"Parsed {file}: {file_metrics}")

    # Build DataFrame: metrics as rows, iterations as columns
    data = {"perf metric": DESIRED_METRICS}
    for idx, iteration in enumerate(iterations, start=1):
        col_name = f"Iteration {idx}"
        col_values = [iteration.get(metric, None) for metric in DESIRED_METRICS]
        data[col_name] = col_values

    df = pd.DataFrame(data)

    # Extract iteration columns
    iteration_cols = [col for col in df.columns if col.startswith("Iteration")]

    # Calculate average, median, and standard deviation across iterations
    df["Average"] = df[iteration_cols].mean(axis=1)
    df["Median"] = df[iteration_cols].median(axis=1)
    df["Standard Deviation"] = df[iteration_cols].std(axis=1)

    # Compute IPC and Branch-miss Rate using the calculated average values
    try:
        cpu_cycles_avg = df.loc[df["perf metric"] == "cpu-cycles", "Average"].values[0]
        instructions_avg = df.loc[df["perf metric"] == "instructions", "Average"].values[0]
        ipc_value = instructions_avg / cpu_cycles_avg if cpu_cycles_avg != 0 else None
    except IndexError:
        ipc_value = None

    try:
        branch_instr_avg = df.loc[df["perf metric"] == "branch-instructions", "Average"].values[0]
        branch_misses_avg = df.loc[df["perf metric"] == "branch-misses", "Average"].values[0]
        branch_miss_rate = branch_misses_avg / branch_instr_avg if branch_instr_avg != 0 else None
    except IndexError:
        branch_miss_rate = None

    # Create new rows for the calculated metrics
    empty_row = {col: None for col in df.columns}
    empty_row["perf metric"] = ""

    # New row for IPC (only the Average column is filled)
    ipc_row = {col: None for col in df.columns}
    ipc_row["perf metric"] = "IPC"
    ipc_row["Average"] = ipc_value

    # New row for Branch-miss Rate (only the Average column is filled)
    bmr_row = {col: None for col in df.columns}
    bmr_row["perf metric"] = "Branch-miss Rate"
    bmr_row["Average"] = branch_miss_rate

    # Add the new rows.
    additional_rows = [empty_row, ipc_row, bmr_row]
    df_extra = pd.DataFrame(additional_rows, columns=df.columns)
    result_df = pd.concat([df, df_extra], ignore_index=True)
    
    # Save final results to an Excel file
    output_file = os.path.join(output_folder, "performance_metrics.xlsx")
    result_df.to_excel(output_file, index=False)
    print(f"Excel file '{output_file}' created successfully.")

if __name__ == '__main__':
    main()
