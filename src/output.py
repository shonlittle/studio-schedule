"""
Output module for the Dance Studio Schedule Optimizer.

This module contains functions for formatting and outputting the schedule.
"""

import os
from datetime import datetime

import pandas as pd


def create_schedule_output(schedule, unscheduled, rooms, teachers, output_dir="."):
    """
    Create Excel output file with schedule information.

    Args:
        schedule (list): List of scheduled class dictionaries.
        unscheduled (list): List of unscheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.
        output_dir (str): Directory to save the output file.

    Returns:
        str: Path to the output file.
    """
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"schedule_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    # Create pandas DataFrame with schedule data
    df = format_schedule_dataframe(schedule, rooms, teachers)

    # Create pandas DataFrame with unscheduled classes
    unscheduled_df = format_unscheduled_dataframe(unscheduled)

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # Write main schedule sheet
        df.to_excel(writer, sheet_name="Schedule", index=False)

        # Write unscheduled classes sheet
        if not unscheduled_df.empty:
            unscheduled_df.to_excel(
                writer, sheet_name="Unscheduled Classes", index=False
            )

        # Create room-based schedule sheets
        create_room_schedule_sheets(writer, schedule, rooms, teachers)

        # Create day-based schedule sheets
        create_day_schedule_sheets(writer, schedule, rooms, teachers)

    return filepath


def format_schedule_dataframe(schedule, rooms, teachers):
    """
    Format schedule data as a pandas DataFrame.

    Args:
        schedule (list): List of scheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.

    Returns:
        DataFrame: Formatted schedule data.
    """
    # Map room and teacher indices to names
    room_names = {i: room["room_name"] for i, room in enumerate(rooms)}
    teacher_names = {i: teacher["teacher_name"] for i, teacher in enumerate(teachers)}

    # Create formatted schedule entries
    formatted_schedule = []
    for entry in schedule:
        formatted_entry = {
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            "Age Range": entry["age_range"],
            "Room": room_names.get(entry["room_idx"], "Unknown"),
            "Teacher": teacher_names.get(entry["teacher_idx"], "Unknown"),
            "Day": entry["day"],
            "Start Time": entry["start_time"],
            "End Time": entry["end_time"],
            "Duration (hours)": entry["duration"],
        }
        formatted_schedule.append(formatted_entry)

    # Create DataFrame
    df = pd.DataFrame(formatted_schedule)

    # Sort by day and start time
    day_order = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    df["Day Order"] = df["Day"].map(day_order)
    df = df.sort_values(by=["Day Order", "Start Time"])
    df = df.drop(columns=["Day Order"])

    return df


def create_room_schedule_sheets(writer, schedule, rooms, teachers):
    """
    Create Excel sheets with room-based schedules.

    Args:
        writer (ExcelWriter): Excel writer object.
        schedule (list): List of scheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.
    """
    # Map room and teacher indices to names
    room_names = {i: room["room_name"] for i, room in enumerate(rooms)}
    teacher_names = {i: teacher["teacher_name"] for i, teacher in enumerate(teachers)}

    # Group schedule by room
    room_schedules = {}
    for entry in schedule:
        room_name = room_names.get(entry["room_idx"], "Unknown")
        if room_name not in room_schedules:
            room_schedules[room_name] = []

        formatted_entry = {
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            "Age Range": entry["age_range"],
            "Teacher": teacher_names.get(entry["teacher_idx"], "Unknown"),
            "Day": entry["day"],
            "Start Time": entry["start_time"],
            "End Time": entry["end_time"],
            "Duration (hours)": entry["duration"],
        }
        room_schedules[room_name].append(formatted_entry)

    # Create a sheet for each room
    for room_name, room_schedule in room_schedules.items():
        # Create DataFrame
        df = pd.DataFrame(room_schedule)

        # Sort by day and start time
        day_order = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }
        df["Day Order"] = df["Day"].map(day_order)
        df = df.sort_values(by=["Day Order", "Start Time"])
        df = df.drop(columns=["Day Order"])

        # Write to Excel
        sheet_name = f"Room - {room_name}"
        if len(sheet_name) > 31:  # Excel sheet name length limit
            sheet_name = sheet_name[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def create_day_schedule_sheets(writer, schedule, rooms, teachers):
    """
    Create Excel sheets with day-based schedules.

    Args:
        writer (ExcelWriter): Excel writer object.
        schedule (list): List of scheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.
    """
    # Map room and teacher indices to names
    room_names = {i: room["room_name"] for i, room in enumerate(rooms)}
    teacher_names = {i: teacher["teacher_name"] for i, teacher in enumerate(teachers)}

    # Group schedule by day
    day_schedules = {}
    for entry in schedule:
        day = entry["day"]
        if day not in day_schedules:
            day_schedules[day] = []

        formatted_entry = {
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            "Age Range": entry["age_range"],
            "Room": room_names.get(entry["room_idx"], "Unknown"),
            "Teacher": teacher_names.get(entry["teacher_idx"], "Unknown"),
            "Start Time": entry["start_time"],
            "End Time": entry["end_time"],
            "Duration (hours)": entry["duration"],
        }
        day_schedules[day].append(formatted_entry)

    # Create a sheet for each day
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for day in day_order:
        if day in day_schedules:
            # Create DataFrame
            df = pd.DataFrame(day_schedules[day])

            # Sort by start time
            df = df.sort_values(by=["Start Time"])

            # Write to Excel
            sheet_name = f"Day - {day}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def format_unscheduled_dataframe(unscheduled):
    """
    Format unscheduled classes data as a pandas DataFrame.

    Args:
        unscheduled (list): List of unscheduled class dictionaries.

    Returns:
        DataFrame: Formatted unscheduled classes data.
    """
    if not unscheduled:
        return pd.DataFrame()

    # Create formatted unscheduled entries
    formatted_unscheduled = []
    for entry in unscheduled:
        formatted_entry = {
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            "Age Range": entry["age_range"],
            "Duration (hours)": entry["duration"],
            "Preferred Days": ", ".join(entry.get("preferred_days", [])),
            "Preferred Rooms": ", ".join(entry.get("preferred_rooms", [])),
            "Preferred Teachers": ", ".join(entry.get("preferred_teachers", [])),
        }
        formatted_unscheduled.append(formatted_entry)

    # Create DataFrame
    df = pd.DataFrame(formatted_unscheduled)

    # Sort by class name
    df = df.sort_values(by=["Class Name"])

    return df


def create_csv_output(schedule, unscheduled, rooms, teachers, output_path="output.csv"):
    """
    Create CSV output file with schedule information.

    Args:
        schedule (list): List of scheduled class dictionaries.
        unscheduled (list): List of unscheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.
        output_path (str): Path to save the CSV file.

    Returns:
        str: Path to the output file.
    """
    # Create pandas DataFrame with schedule data
    df = format_schedule_dataframe(schedule, rooms, teachers)

    # Map room and teacher indices to names for later use
    room_names = {i: room["room_name"] for i, room in enumerate(rooms)}
    teacher_names = {i: teacher["teacher_name"] for i, teacher in enumerate(teachers)}

    # Check for duplicates and conflicts
    df = check_and_fix_conflicts(df)
    removed_classes = (
        []
    )  # Initialize empty list since we're not getting it from check_and_fix_conflicts

    # Add removed classes to unscheduled list
    for class_info in removed_classes:
        # Find the original class in the schedule
        for entry in schedule:
            room_name = room_names.get(entry["room_idx"], "Unknown")
            if (
                entry["class_name"] == class_info["class_name"]
                and entry["day"] == class_info["day"]
                and room_name == class_info["room"]
            ):

                # Create unscheduled class entry
                unscheduled_class = {
                    "class_name": entry["class_name"],
                    "style": entry.get("style", ""),
                    "level": entry.get("level", ""),
                    "age_range": entry["age_range"],
                    "duration": entry["duration"],
                    "preferred_days": entry.get("preferred_days", []),
                    "preferred_rooms": entry.get("preferred_rooms", []),
                    "preferred_teachers": entry.get("preferred_teachers", []),
                    "reason": f"Removed due to conflict in {class_info['room']} on {class_info['day']}",
                }

                unscheduled.append(unscheduled_class)
                break

    # Create pandas DataFrame with unscheduled classes
    unscheduled_df = format_unscheduled_dataframe(unscheduled)

    # Save to CSV
    df.to_csv(output_path, index=False)

    # Save unscheduled classes to a separate CSV if there are any
    if not unscheduled_df.empty:
        unscheduled_path = output_path.replace(".csv", "_unscheduled.csv")
        unscheduled_df.to_csv(unscheduled_path, index=False)
        print(f"Unscheduled classes saved to '{unscheduled_path}'.")

    return output_path


def check_and_fix_conflicts(df):
    """
    Check for and fix conflicts in the schedule.

    Args:
        df (DataFrame): Schedule data.

    Returns:
        DataFrame: Cleaned schedule data.
    """
    # Check for exact duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    dup_count = initial_count - len(df)
    if dup_count > 0:
        print(f"Removed {dup_count} duplicate entries from the schedule.")

    # Check for room conflicts (same room, same day, overlapping time)
    conflicts = []
    classes_to_remove = set()

    # Group by room and day
    for (room, day), group in df.groupby(["Room", "Day"]):
        if len(group) <= 1:
            continue

        # Sort by start time
        sorted_classes = group.sort_values("Start Time").reset_index()

        # Check for overlaps
        for i in range(len(sorted_classes) - 1):
            current_end = sorted_classes.loc[i, "End Time"]
            next_start = sorted_classes.loc[i + 1, "Start Time"]

            if current_end > next_start:
                conflicts.append(
                    {
                        "Room": room,
                        "Day": day,
                        "Class1": sorted_classes.loc[i, "Class Name"],
                        "End1": current_end,
                        "Class2": sorted_classes.loc[i + 1, "Class Name"],
                        "Start2": next_start,
                    }
                )

                # Mark the second class for removal to resolve the conflict
                # We'll keep the first class in each conflict
                classes_to_remove.add(
                    (room, day, sorted_classes.loc[i + 1, "Class Name"])
                )

    # Remove conflicting classes
    if classes_to_remove:
        print(f"\nRemoving {len(classes_to_remove)} classes to resolve time conflicts:")
        for room, day, class_name in classes_to_remove:
            print(f"  Removing '{class_name}' from Room {room} on {day}")
            df = df[
                ~(
                    (df["Room"] == room)
                    & (df["Day"] == day)
                    & (df["Class Name"] == class_name)
                )
            ]

    # Report any remaining conflicts
    remaining_conflicts = []
    for (room, day), group in df.groupby(["Room", "Day"]):
        if len(group) <= 1:
            continue

        # Sort by start time
        sorted_classes = group.sort_values("Start Time").reset_index()

        # Check for overlaps
        for i in range(len(sorted_classes) - 1):
            current_end = sorted_classes.loc[i, "End Time"]
            next_start = sorted_classes.loc[i + 1, "Start Time"]

            if current_end > next_start:
                remaining_conflicts.append(
                    {
                        "Room": room,
                        "Day": day,
                        "Class1": sorted_classes.loc[i, "Class Name"],
                        "End1": current_end,
                        "Class2": sorted_classes.loc[i + 1, "Class Name"],
                        "Start2": next_start,
                    }
                )

    # Report remaining conflicts
    if remaining_conflicts:
        print(
            f"\nWARNING: Found {len(remaining_conflicts)} remaining time conflicts in the schedule:"
        )
        for conflict in remaining_conflicts:
            print(
                f"  Room {conflict['Room']} on {conflict['Day']}: "
                f"'{conflict['Class1']}' (ends {conflict['End1']}) overlaps with "
                f"'{conflict['Class2']}' (starts {conflict['Start2']})"
            )

    # Check for accordion wall conflicts
    accordion_conflicts = []

    # Define room groups
    accordion_groups = {
        "Group 1": ["Room 1", "Room 2", "Room 1+2"],
        "Group 2": ["Room 3", "Room 4", "Room 3+4"],
    }

    # Check each group
    for group_name, rooms in accordion_groups.items():
        # Filter for classes in these rooms
        group_df = df[df["Room"].isin(rooms)]

        # Group by day
        for day, day_group in group_df.groupby("Day"):
            # Check each class against others on the same day
            for idx1, row1 in day_group.iterrows():
                for idx2, row2 in day_group.iterrows():
                    if idx1 >= idx2:
                        continue

                    # Skip if same room (already checked above)
                    if row1["Room"] == row2["Room"]:
                        continue

                    # Check if one room is a combined room that includes the other
                    room1 = row1["Room"]
                    room2 = row2["Room"]

                    # Check if rooms conflict (e.g., Room 1 and Room 1+2)
                    rooms_conflict = False
                    if "+" in room1:
                        components = room1.split("+")
                        if room2 in components or room2.strip() in [
                            c.strip() for c in components
                        ]:
                            rooms_conflict = True
                    elif "+" in room2:
                        components = room2.split("+")
                        if room1 in components or room1.strip() in [
                            c.strip() for c in components
                        ]:
                            rooms_conflict = True

                    # If rooms conflict, check for time overlap
                    if rooms_conflict:
                        # Check for time overlap
                        if (
                            row1["Start Time"] < row2["End Time"]
                            and row2["Start Time"] < row1["End Time"]
                        ):
                            accordion_conflicts.append(
                                {
                                    "Day": day,
                                    "Room1": room1,
                                    "Class1": row1["Class Name"],
                                    "Time1": f"{row1['Start Time']} - {row1['End Time']}",
                                    "Room2": room2,
                                    "Class2": row2["Class Name"],
                                    "Time2": f"{row2['Start Time']} - {row2['End Time']}",
                                }
                            )

    # Report accordion wall conflicts
    if accordion_conflicts:
        print(f"\nWARNING: Found {len(accordion_conflicts)} accordion wall conflicts:")
        for conflict in accordion_conflicts:
            print(
                f"  {conflict['Day']}: Room {conflict['Room1']} "
                f"('{conflict['Class1']}', {conflict['Time1']}) conflicts with "
                f"Room {conflict['Room2']} ('{conflict['Class2']}', {conflict['Time2']})"
            )

    return df
