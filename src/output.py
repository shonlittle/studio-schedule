"""
Output module for the Dance Studio Schedule Optimizer.

This module contains functions for generating output files with schedule
information, including both scheduled and unscheduled classes.
"""

import os
from datetime import datetime

import pandas as pd


def create_schedule_output(
    scheduled_classes,
    unscheduled_classes,
    rooms,
    teacher_specializations,
    output_dir="output",
    teacher_names=None,
):
    """
    Create Excel output file with schedule information.

    Args:
        scheduled_classes (list): List of scheduled class dictionaries.
        unscheduled_classes (list): List of unscheduled class dictionaries.
        rooms (list): List of room data dictionaries.
        teacher_specializations (dict): Dictionary of teacher specializations.
        output_dir (str): Directory to save output files.
        teacher_names (dict, optional): Dictionary of teacher ID to name
            mappings. If None, names from specs will be used.

    Returns:
        str: Path to the created output file.
    """
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"schedule_{timestamp}.xlsx"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Create room and teacher name mappings
    room_names = {room["room_id"]: room["room_name"] for room in rooms}

    # Use provided teacher_names if available,
    # otherwise create from specializations
    if teacher_names is None:
        teacher_names = {}
        for teacher_id in teacher_specializations.keys():
            # Extract teacher name from specializations
            if "name" in teacher_specializations[teacher_id]:
                name_list = teacher_specializations[teacher_id]["name"]
                teacher_names[teacher_id] = name_list[0]
            else:
                teacher_names[teacher_id] = f"Teacher {teacher_id}"

    # Format scheduled classes
    formatted_schedule = []
    for entry in scheduled_classes:
        formatted_entry = {
            "Class ID": entry["class_id"],
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            # Format age range
            "Age Range": format_age_range(entry),
            "Day": entry["day"],
            "Start Time": entry["start_time"],
            "End Time": entry["end_time"],
            "Duration (hours)": entry["duration"],
            "Room": room_names.get(entry["room_id"], "Unknown"),
            "Teacher ID": entry["teacher_id"],
            # Get teacher name or default to "Unassigned"
            "Teacher Name": get_teacher_name(teacher_names, entry),
        }
        formatted_schedule.append(formatted_entry)

    # Create DataFrame
    schedule_df = pd.DataFrame(formatted_schedule)

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

    if not schedule_df.empty:
        schedule_df["Day Order"] = schedule_df["Day"].map(day_order)
        schedule_df = schedule_df.sort_values(by=["Day Order", "Start Time"])
        schedule_df = schedule_df.drop(columns=["Day Order"])

    # Format unscheduled classes
    formatted_unscheduled = []
    for entry in unscheduled_classes:
        formatted_entry = {
            "Class ID": entry["class_id"],
            "Class Name": entry["class_name"],
            "Style": entry["style"],
            "Level": entry["level"],
            # Format age range
            "Age Range": format_age_range(entry),
            "Duration (hours)": entry["duration"],
            "Reason": entry.get("reason", "Unknown"),
        }
        formatted_unscheduled.append(formatted_entry)

    # Create DataFrame
    unscheduled_df = pd.DataFrame(formatted_unscheduled)

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # Write main schedule sheet
        schedule_df.to_excel(writer, sheet_name="Schedule", index=False)

        # Write unscheduled classes sheet
        if not unscheduled_df.empty:
            sheet_name = "Unscheduled Classes"
            unscheduled_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Create room-based schedule sheets
        create_room_schedule_sheets(writer, schedule_df)

        # Create day-based schedule sheets
        create_day_schedule_sheets(writer, schedule_df)

    return filepath


def create_room_schedule_sheets(writer, schedule_df):
    """
    Create Excel sheets with room-based schedules.

    Args:
        writer: Excel writer object.
        schedule_df (DataFrame): DataFrame with schedule information.
    """
    # Skip if schedule is empty
    if schedule_df.empty:
        return

    # Group by room
    for room, group in schedule_df.groupby("Room"):
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
        group["Day Order"] = group["Day"].map(day_order)
        group = group.sort_values(by=["Day Order", "Start Time"])
        group = group.drop(columns=["Day Order"])

        # Write to Excel
        sheet_name = f"Room - {room}"
        if len(sheet_name) > 31:  # Excel sheet name length limit
            sheet_name = sheet_name[:31]
        group.to_excel(writer, sheet_name=sheet_name, index=False)


def get_teacher_name(teacher_names, entry):
    """
    Get teacher name from mapping or return default.

    Args:
        teacher_names (dict): Mapping of teacher IDs to names.
        entry (dict): Class entry with teacher_id.

    Returns:
        str: Teacher name or "Unassigned" if not found.
    """
    return teacher_names.get(entry["teacher_id"], "Unassigned")


def format_age_range(entry):
    """
    Format age range as a string.

    Args:
        entry (dict): Class entry with age_start and age_end.

    Returns:
        str: Formatted age range.
    """
    return f"{entry['age_start']}-{entry['age_end']}"


def create_day_schedule_sheets(writer, schedule_df):
    """
    Create Excel sheets with day-based schedules.

    Args:
        writer: Excel writer object.
        schedule_df (DataFrame): DataFrame with schedule information.
    """
    # Skip if schedule is empty
    if schedule_df.empty:
        return

    # Group by day
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
        if day in schedule_df["Day"].values:
            group = schedule_df[schedule_df["Day"] == day]

            # Sort by start time
            group = group.sort_values(by=["Start Time"])

            # Write to Excel
            sheet_name = f"Day - {day}"
            group.to_excel(writer, sheet_name=sheet_name, index=False)
