"""
Data loader module for the Dance Studio Schedule Optimizer.

This module contains functions for loading and parsing data from the
normalized Excel structure.
"""

from datetime import datetime, timedelta

import pandas as pd


def parse_time_value(time_value):
    """
    Parse a time value that could be either a string or a datetime.time object.

    Args:
        time_value: Either a string in format "HH:MM" or a datetime.time object

    Returns:
        datetime: A datetime object representing the time
    """
    if isinstance(time_value, str):
        return datetime.strptime(time_value, "%H:%M")
    else:
        # Already a time object, convert to datetime
        return datetime.combine(datetime.today(), time_value)


def load_data(file_path):
    """
    Load data from the normalized Excel structure.

    Args:
        file_path (str): Path to the Excel file containing schedule data.

    Returns:
        dict: Dictionary containing all loaded data structures.
    """
    # Define sheet names
    classes_sheet = "classes"
    room_avail_sheet = "room_availability"
    room_config_sheet = "room_configurations"
    teacher_avail_sheet = "teacher_availability"
    teacher_spec_sheet = "teacher_specializations"
    class_pref_sheet = "class_preferences"

    # Load classes sheet
    classes_df = load_excel_sheet(file_path, classes_sheet)

    # Load all sheets
    sheets = {
        "room_avail": room_avail_sheet,
        "room_config": room_config_sheet,
        "teacher_avail": teacher_avail_sheet,
        "teacher_spec": teacher_spec_sheet,
        "class_pref": class_pref_sheet,
    }

    # Load each sheet
    room_availability_df = load_excel_sheet(file_path, sheets["room_avail"])
    room_configs_df = load_excel_sheet(file_path, sheets["room_config"])
    teacher_availability_df = load_excel_sheet(file_path, sheets["teacher_avail"])
    teacher_specializations_df = load_excel_sheet(file_path, sheets["teacher_spec"])
    class_preferences_df = load_excel_sheet(file_path, sheets["class_pref"])

    # Process classes
    classes = []
    for _, row in classes_df.iterrows():
        class_data = {
            "class_id": int(row["class_id"]),
            "class_name": row["class_name"],
            "style": row["style"],
            "level": row["level"],
            "age_start": row["age_start"],
            "age_end": row["age_end"],
            "duration": row["duration"],
            # Convert hours to 15-minute slots (e.g., 1.5 hours = 6 slots)
            "duration_slots": int(row["duration"] * 4),
        }
        classes.append(class_data)

    # Process room configurations
    rooms = []
    for _, row in room_configs_df.iterrows():
        room_data = {
            "room_id": int(row["room_id"]),
            "room_name": row["room_name"],
            "is_combined": bool(row["is_combined"]),
            "component_rooms": (
                row["component_rooms"].split(",")
                if not pd.isna(row["component_rooms"])
                else None
            ),
            "group": row.get("group", None),
        }
        rooms.append(room_data)

    # Create room name to ID mapping
    room_name_to_id = {room["room_name"]: room["room_id"] for room in rooms}

    # Process room availability
    room_availability = {}
    for _, row in room_availability_df.iterrows():
        room_id = int(row["room_id"])
        day = row["day"]
        day_idx = day_to_index(day)

        # Convert time range to slots
        start_time = parse_time_value(row["start_time"])
        end_time = parse_time_value(row["end_time"])

        # Create 15-minute slots
        current_time = start_time
        while current_time < end_time:
            slot_idx = time_to_slot_index(current_time)

            # Mark this slot as available
            room_availability[(room_id, day_idx, slot_idx)] = True

            # Move to next slot
            current_time += timedelta(minutes=15)

    # Process teacher availability (similar to room availability)
    teacher_availability = {}
    teacher_names = {}  # Create a mapping from teacher_id to teacher_name

    for _, row in teacher_availability_df.iterrows():
        teacher_id = int(row["teacher_id"])
        day = row["day"]
        day_idx = day_to_index(day)

        # Store teacher name if available
        if "teacher_name" in row and not pd.isna(row["teacher_name"]):
            teacher_names[teacher_id] = row["teacher_name"]

        # Convert time range to slots
        start_time = parse_time_value(row["start_time"])
        end_time = parse_time_value(row["end_time"])

        # Create 15-minute slots
        current_time = start_time
        while current_time < end_time:
            slot_idx = time_to_slot_index(current_time)

            # Mark this slot as available
            teacher_availability[(teacher_id, day_idx, slot_idx)] = True

            # Move to next slot
            current_time += timedelta(minutes=15)

    # Process class preferences
    class_preferences = {}
    for _, row in class_preferences_df.iterrows():
        class_id = int(row["class_id"])
        pref_type = row["preference_type"]
        pref_value = row["preference_value"]
        weight = row["weight"]

        if class_id not in class_preferences:
            class_preferences[class_id] = {}

        if pref_type not in class_preferences[class_id]:
            class_preferences[class_id][pref_type] = []

        # For room preferences, convert room names to IDs if they're strings
        if (
            pref_type == "room"
            and isinstance(pref_value, str)
            and pref_value in room_name_to_id
        ):
            pref_value = room_name_to_id[pref_value]

        # For time preferences, convert time ranges to slot indices
        if pref_type == "time" and isinstance(pref_value, str) and "-" in pref_value:
            try:
                start_time_str, end_time_str = pref_value.split("-")
                start_time = datetime.strptime(start_time_str, "%H:%M")
                end_time = datetime.strptime(end_time_str, "%H:%M")

                # Convert to slot indices
                start_slot = time_to_slot_index(start_time)
                end_slot = time_to_slot_index(end_time)

                # Create a list of all slots in the range
                slots = list(range(start_slot, end_slot))

                # Add each slot as a separate preference
                for slot in slots:
                    class_preferences[class_id][pref_type].append(
                        {"value": slot, "weight": weight}
                    )

                # Skip adding the original time range preference
                continue
            except Exception as e:
                # If parsing fails, keep the original value
                # Log parsing error
                # Handle parsing error
                error_prefix = "Warning: Cannot parse"
                error_msg = f"{error_prefix} '{pref_value}'"
                # Very short truncation to avoid line length issues
                err_short = str(e)[:20]
                print(f"{error_msg}: {err_short}")

        # Create preference object
        pref_obj = {"value": pref_value, "weight": weight}
        # Add to preferences list
        class_preferences[class_id][pref_type].append(pref_obj)

    # Process teacher specializations
    teacher_specializations = {}
    for _, row in teacher_specializations_df.iterrows():
        teacher_id = int(row["teacher_id"])
        spec_type = row["specialization_type"]
        spec_value = row["specialization_value"]

        if teacher_id not in teacher_specializations:
            teacher_specializations[teacher_id] = {}

        if spec_type not in teacher_specializations[teacher_id]:
            teacher_specializations[teacher_id][spec_type] = []

        # Get the specialization list and append the value
        spec_list = teacher_specializations[teacher_id][spec_type]
        spec_list.append(spec_value)

    return {
        "classes": classes,
        "rooms": rooms,
        "room_availability": room_availability,
        "teacher_availability": teacher_availability,
        "class_preferences": class_preferences,
        "teacher_specializations": teacher_specializations,
        "teacher_names": teacher_names,  # Add teacher names mapping
    }


def load_excel_sheet(file_path, sheet_name):
    """
    Load an Excel sheet into a pandas DataFrame.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to load.

    Returns:
        DataFrame: Loaded data.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)


def day_to_index(day):
    """
    Convert day name to index (0=Monday, 1=Tuesday, etc.).

    Args:
        day (str): Day name.

    Returns:
        int: Day index.
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


def time_to_slot_index(time):
    """
    Convert time to slot index (0=00:00, 1=00:15, etc.).

    Args:
        time (datetime): Time object.

    Returns:
        int: Slot index.
    """
    return time.hour * 4 + time.minute // 15


def slot_index_to_time(slot_index):
    """
    Convert slot index to time string.

    Args:
        slot_index (int): Slot index.

    Returns:
        str: Time string in format HH:MM.
    """
    hours = slot_index // 4
    minutes = (slot_index % 4) * 15
    return f"{hours:02d}:{minutes:02d}"
