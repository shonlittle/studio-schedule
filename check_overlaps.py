import pandas as pd

# Load the schedule
df = pd.read_excel("output/schedule_20250517_161953.xlsx", sheet_name="Schedule")

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
        print(
            f"Class 1: {df.iloc[i]['Class Name']} in {df.iloc[i]['Room']} on {df.iloc[i]['Day']} from {df.iloc[i]['Start Time']} to {df.iloc[i]['End Time']}"
        )
        print(
            f"Class 2: {df.iloc[j]['Class Name']} in {df.iloc[j]['Room']} on {df.iloc[j]['Day']} from {df.iloc[j]['Start Time']} to {df.iloc[j]['End Time']}"
        )
