"""
Data loader module for the Dance Studio Schedule Optimizer.

This module contains functions for loading and parsing data from the Excel
file.
"""

from datetime import datetime, timedelta

import pandas as pd


def load_data(file_path):
    """
    Load data from Excel file and return structured data objects.

    Args:
        file_path (str): Path to the Excel file containing schedule data.

    Returns:
        tuple: (classes, teachers, rooms) data structures.
    """
    # Load Excel sheets using pandas
    try:
        classes_df = pd.read_excel(file_path, sheet_name="classes")
        teachers_df = pd.read_excel(file_path, sheet_name="teachers")
        rooms_df = pd.read_excel(file_path, sheet_name="rooms")
    except Exception as e:
        raise ValueError(f"Error loading Excel file: {e}")

    # Process classes data
    classes = []
    for _, row in classes_df.iterrows():
        class_data = {
            "class_name": row["class_name"],
            "style": row["style"] if "style" in row else "",
            "level": row["level"] if "level" in row else "",
            "age_start": row["age_start"] if "age_start" in row else 0,
            "age_end": row["age_end"] if "age_end" in row else 99,
            "duration": row["duration"],  # in hours
            # convert to 15-min slots
            "duration_slots": int(row["duration"] * 4),
            "preferred_days": (
                row["preferred_days"].split(",")
                if isinstance(row["preferred_days"], str)
                else []
            ),
            "preferred_time_ranges": (
                parse_time_ranges(row["preferred_time_ranges"])
                if isinstance(row["preferred_time_ranges"], str)
                else {}
            ),
            "preferred_rooms": (
                row["preferred_rooms"].split(",")
                if isinstance(row["preferred_rooms"], str)
                else []
            ),
            "preferred_teachers": (
                row["preferred_teachers"].split(",")
                if isinstance(row["preferred_teachers"], str)
                else []
            ),
        }
        classes.append(class_data)

    # Process teachers data
    teachers = []
    for _, row in teachers_df.iterrows():
        teacher_data = {
            "teacher_name": row["teacher_name"],
            "availability": (
                parse_availability(row["availability"])
                if isinstance(row["availability"], str)
                else {}
            ),
        }
        teachers.append(teacher_data)

    # Process rooms data
    rooms = []
    for _, row in rooms_df.iterrows():
        room_data = {
            "room_name": row["room_name"],
            "availability": (
                parse_availability(row["availability"])
                if isinstance(row["availability"], str)
                else {}
            ),
            "group": row["group"] if "group" in row else None,
        }
        rooms.append(room_data)

    return classes, teachers, rooms


def parse_availability(availability_str):
    """
    Parse availability string in format 'Day:Start-End,Day:Start-End,...'

    Args:
        availability_str (str): Availability string.

    Returns:
        dict: Dictionary mapping days to lists of available time slots.
    """
    availability = {}

    # Split by comma to get day entries
    day_entries = availability_str.split(",")

    for entry in day_entries:
        # Split by colon to separate day and time range
        parts = entry.strip().split(":")
        if len(parts) != 2:
            continue

        day, time_range = parts
        day = day.strip()

        # Split time range by hyphen
        time_parts = time_range.strip().split("-")
        if len(time_parts) != 2:
            continue

        start_time, end_time = time_parts

        # Convert times to slot indices
        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")

            # Calculate slot indices
            slots = convert_to_time_slots(start_dt, end_dt)

            # Add to availability dictionary
            availability[day] = slots
        except ValueError:
            # Skip invalid time formats
            continue

    return availability


def parse_time_ranges(time_ranges_str):
    """
    Parse time ranges string for class preferences.

    Args:
        time_ranges_str (str): Time ranges string.

    Returns:
        dict: Dictionary mapping days to lists of preferred time slots.
    """
    # This is similar to parse_availability but might have a different format
    # For now, we'll assume the same format
    return parse_availability(time_ranges_str)


def convert_to_time_slots(start_time, end_time, slot_duration=15):
    """
    Convert time range to list of 15-minute time slots.

    Args:
        start_time (datetime): Start time.
        end_time (datetime): End time.
        slot_duration (int): Duration of each slot in minutes.

    Returns:
        list: List of slot indices.
    """
    # Reference time (15:15)
    reference_time = datetime.strptime("15:15", "%H:%M")

    # Calculate start and end slots
    start_delta = (start_time.hour - reference_time.hour) * 60 + (
        start_time.minute - reference_time.minute
    )
    end_delta = (end_time.hour - reference_time.hour) * 60 + (
        end_time.minute - reference_time.minute
    )

    start_slot = max(0, start_delta // slot_duration)
    end_slot = max(0, end_delta // slot_duration)

    # Generate list of slots
    return list(range(start_slot, end_slot))


def time_slot_to_time(slot_index, slot_duration=15):
    """
    Convert slot index to time string.

    Args:
        slot_index (int): Slot index.
        slot_duration (int): Duration of each slot in minutes.

    Returns:
        str: Time string in format HH:MM.
    """
    # Reference time (15:15)
    reference_time = datetime.strptime("15:15", "%H:%M")

    # Calculate time
    slot_time = reference_time + timedelta(minutes=slot_index * slot_duration)

    return slot_time.strftime("%H:%M")


def day_to_index(day):
    """
    Convert day name to index.

    Args:
        day (str): Day name.

    Returns:
        int: Day index (0 = Monday, 1 = Tuesday, etc.).
    """
    days = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    return days.get(day, -1)


def index_to_day(index):
    """
    Convert day index to name.

    Args:
        index (int): Day index.

    Returns:
        str: Day name.
    """
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    if 0 <= index < len(days):
        return days[index]
    return None
