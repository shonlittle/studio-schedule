"""
Data fix utility for the Dance Studio Schedule Optimizer.

This script fixes data issues in the schedule data file, specifically
replacing 'ctu' values in the end_time column with '21:00'.
"""

import pandas as pd

# Read the room_availability sheet
df = pd.read_excel("data/schedule-data.xlsx", sheet_name="room_availability")

# Fix the 'ctu' value
df.loc[df["end_time"] == "ctu", "end_time"] = "21:00"

# Define the input/output file path
file_path = "data/schedule-data.xlsx"

# Get all sheet names from the original file
sheet_names = pd.ExcelFile(file_path).sheet_names

# Create a new Excel writer using a context manager for proper cleanup
with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
    # Copy all sheets from the original file to the new file
    for sheet_name in sheet_names:
        # Read the sheet
        sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)

        # If it's the room_availability sheet, use our fixed version
        if sheet_name == "room_availability":
            sheet_df = df

        # Write the sheet to the new file
        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Fixed data file saved.")
