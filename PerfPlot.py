import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Order for the performance metrics:
metrics_order = [
    "IPC (Instructions per Cycle)",
    "Branch-miss Rate",
    "Stall Cycles",
    "LFENCE Barrier Rate"
]

# Match Excel file
metric_name_mapping = {
    "IPC": "IPC (Instructions per Cycle)",
    "Branch-miss Rate": "Branch-miss Rate",
    "cycle_activity.stalls_total": "Stall Cycles",
    "misc2_retired.lfence": "LFENCE Barrier Rate"
}

# Taths to point to each Excel files, for each kernel Config.
kernel_files = {
    "Spectre V1": "",
    "Spectre V2": "",
    "Speculative Store Bypass": "",
    "Secure Kernel": ""
}

# Create a base DataFrame.
df = pd.DataFrame({"Perf Metric": metrics_order})

perf_metric_column = "perf metric"

# Process each kernel’s file:
for kernel, file_path in kernel_files.items():
    df_kernel = pd.read_excel(file_path)
    
    print(f"Columns in {file_path}: {df_kernel.columns.tolist()}")
    
    df_kernel_filtered = df_kernel[df_kernel[perf_metric_column].isin(metric_name_mapping.keys())].copy()
    
    df_kernel_filtered[perf_metric_column] = df_kernel_filtered[perf_metric_column].map(metric_name_mapping)
    
    df_kernel_filtered["Degradation (%)"] = pd.to_numeric(
        df_kernel_filtered["Degradation (%)"].astype(str).str.replace(",", "."),
        errors="coerce"
    )
    
    df_kernel_filtered = df_kernel_filtered.dropna(subset=["Degradation (%)"])
    
    # Order the rows
    df_kernel_filtered["Perf Metric"] = pd.Categorical(
        df_kernel_filtered[perf_metric_column],
        categories=metrics_order,
        ordered=True
    )
    df_kernel_filtered = df_kernel_filtered.sort_values("Perf Metric")
    
    # Add the degradation values 
    df[kernel] = df_kernel_filtered["Degradation (%)"].values

# Reshape the DataFrame for plotting.
df_melted = df.melt(id_vars="Perf Metric", var_name="Kernel", value_name="Value")

# Kernel order.
hue_order = ["Spectre V1", "Spectre V2", "Speculative Store Bypass", "Secure Kernel"]

# Color Palette.
custom_palette = [plt.cm.tab20.colors[i] for i in [4, 12, 2, 0]]

# Create the vertical bar plot.
plt.figure(figsize=(12, 8))
ax = sns.barplot(
    data=df_melted,
    x="Perf Metric",
    y="Value",
    hue="Kernel",
    hue_order=hue_order,
    palette=custom_palette
)

# Horizontal line at y=0.
plt.axhline(y=0, color="black", linewidth=2)

# Add labels to the end of each bar.
# For "IPC (Instructions per Cycle)": label red if value > 0, green otherwise.
# For other metrics: label red if value < 0, green otherwise.
for index, (value, test_name) in enumerate(zip(df_melted["Value"], df_melted["Perf Metric"])):
    if "IPC" in test_name:
        label_color = "red" if value > 0 else "green"
        ha_position = 'left' if value > 0 else 'right'
        x_offset = -0.095 if value > 0 else 0.095
        y_offset = 2 if value > 0 else -2
    else:
        label_color = "red" if value < 0 else "green"
        ha_position = 'right' if value < 0 else 'left'
        x_offset = 0.095 if value < 0 else -0.095
        y_offset = -2 if value < 0 else 2

    bar = ax.patches[index]
    bar_x = bar.get_x() + bar.get_width() / 2
    label_y_position = bar.get_y() + bar.get_height()

    plt.text(
        bar_x + x_offset,
        label_y_position + y_offset,
        f"{value:.2f}%",
        ha=ha_position,
        va='center',
        fontsize=10.5,
        color=label_color
    )

# Customize
plt.title("Performance Degradation Across Kernels", fontsize=16)
plt.ylabel("Degradation (%)", fontsize=14)
plt.xlabel("Perf Metric", fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.legend(title="Kernel", fontsize=12, title_fontsize=14, loc="lower left")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Save the plot as PNG file.
output_path = ""
plt.savefig(output_path, format='png', dpi=600, bbox_inches='tight')
print(f"High-resolution vertical image saved to {output_path}")

# Display the plot.
plt.show()
