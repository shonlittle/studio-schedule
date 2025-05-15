"""
Output module for the Dance Studio Schedule Optimizer.

This module contains functions for formatting and outputting the schedule.
"""

import os
from datetime import datetime

import pandas as pd


def create_schedule_output(schedule, rooms, teachers, output_dir="."):
    """
    Create Excel output file with schedule information.

    Args:
        schedule (list): List of scheduled class dictionaries.
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

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # Write main schedule sheet
        df.to_excel(writer, sheet_name="Schedule", index=False)

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
