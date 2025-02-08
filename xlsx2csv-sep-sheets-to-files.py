import pandas as pd

# Path to your Excel file
xlsx_file = './2024-QS-by-Subject.xlsx'

# Read all sheets into a dictionary: keys are sheet names, values are DataFrames
all_sheets = pd.read_excel(xlsx_file, sheet_name=None)

# Loop through the dictionary and save each sheet as a CSV file
for sheet_name, df in all_sheets.items():
    csv_file_name = f"{sheet_name}.csv"
    df.to_csv(csv_file_name, index=False)
    print(f"Saved {csv_file_name}")
