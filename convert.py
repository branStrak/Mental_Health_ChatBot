#This script converts the mental health conversational dataset into a format suitable for AutoTrain.
#It reads the original CSV, cleans it, and saves a new CSV with 'instruction', 'input', and 'output' columns.

import pandas as pd

input_file = "./mental_health_conversational_dataset.csv"
output_file = "mental_health_autotrain_ready.csv"

clean_rows = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if "#response" in line or not line.strip():
            continue  # skip header/empty
        if "#" in line:
            parts = line.strip().split("#", 1)
            if len(parts) == 2:
                instruction, output = parts
                clean_rows.append({
                    "instruction": instruction.strip(),
                    "input": "",  # leave blank if not used
                    "output": output.strip()
                })

# Step 2: Create a DataFrame and save it
df_cleaned = pd.DataFrame(clean_rows)
df_cleaned.to_csv(output_file, index=False)

print(f"✅ Cleaned dataset saved to: {output_file}")
