import os
import pandas as pd

# Path to csv all results folder
folder_path = "results_parse"

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

# Initialize an empty DataFrame
combined_df = pd.DataFrame()

for i, file in enumerate(sorted(csv_files)):
    file_path = os.path.join(folder_path, file)
    try:
        # Open the file with error ignoring
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            df = pd.read_csv(f)

        # Use the file name (without .csv) as column label
        label = os.path.splitext(file)[0]

        if i == 0:
            # Add both columns for the first file
            combined_df["ID"] = df.iloc[:, 0]
            combined_df[label] = df.iloc[:, 1]
        else:
            # Only add the second column for subsequent files
            combined_df[label] = df.iloc[:, 1]
    except Exception as e:
        print(f"Failed to read {file}: {e}")

# Save the combined CSV
combined_df.to_csv("all_results.csv", index=False, encoding="utf-8")

print("Combined CSV saved as 'all_results.csv'")
