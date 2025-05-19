"""
Overlap detection utility for the Dance Studio Schedule Optimizer.

This script checks for overlapping classes in the generated schedule,
which would indicate scheduling conflicts that need to be resolved.
"""

import pandas as pd

# Load the schedule
# File path to the schedule
schedule_file = "output/schedule_20250517_161953.xlsx"
df = pd.read_excel(schedule_file, sheet_name="Schedule")

# Convert time strings to datetime objects for comparison
df["Start"] = pd.to_datetime(df["Start Time"], format="%H:%M").dt.time
df["End"] = pd.to_datetime(df["End Time"], format="%H:%M").dt.time

# Check for overlapping classes
overlaps = []
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        # Check if same room and day
        if (
            df.iloc[i]["Room"] == df.iloc[j]["Room"]
            and df.iloc[i]["Day"] == df.iloc[j]["Day"]
        ):
            # Check if time periods overlap
            if (
                df.iloc[i]["Start"] < df.iloc[j]["End"]
                and df.iloc[j]["Start"] < df.iloc[i]["End"]
            ):
                overlaps.append((i, j))

print(f"Found {len(overlaps)} overlapping classes")

# Print details of overlapping classes
if overlaps:
    print("\nOverlapping classes:")
    for i, j in overlaps[:5]:  # Show up to 5 examples
        print(f"\nOverlap {i+1} vs {j+1}:")
        class1 = df.iloc[i]
        class2 = df.iloc[j]
        # Format class details for printing
        class1_details = (
            f"Class 1: {class1['Class Name']} in {class1['Room']} "
            f"on {class1['Day']} from {class1['Start Time']} "
            f"to {class1['End Time']}"
        )
        class2_details = (
            f"Class 2: {class2['Class Name']} in {class2['Room']} "
            f"on {class2['Day']} from {class2['Start Time']} "
            f"to {class2['End Time']}"
        )
        print(class1_details)
        print(class2_details)
