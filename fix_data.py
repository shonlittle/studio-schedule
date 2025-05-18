import pandas as pd

# Read the room_availability sheet
df = pd.read_excel("data/schedule-data.xlsx", sheet_name="room_availability")

# Fix the 'ctu' value
df.loc[df["end_time"] == "ctu", "end_time"] = "21:00"

# Create a new Excel writer
writer = pd.ExcelWriter("data/schedule-data-fixed.xlsx", engine="openpyxl")

# Copy all sheets from the original file to the new file
for sheet_name in pd.ExcelFile("data/schedule-data.xlsx").sheet_names:
    # Read the sheet
    sheet_df = pd.read_excel("data/schedule-data.xlsx", sheet_name=sheet_name)

    # If it's the room_availability sheet, use our fixed version
    if sheet_name == "room_availability":
        sheet_df = df

    # Write the sheet to the new file
    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

# Save the file
writer.close()

print("Fixed data file saved.")
