"""
Room scheduler module for the Dance Studio Schedule Optimizer.

This module contains functions for creating the room availability matrix
and assigning classes to room-time slots (Phases 1 & 2).
"""

from data_loader import index_to_day, slot_index_to_time


def create_room_availability_matrix(rooms, room_availability):
    """
    Create the room time slot availability matrix with conflict handling.

    Args:
        rooms (list): List of room data dictionaries.
        room_availability (dict): Dictionary mapping (room_id, day_idx, slot_idx) to availability.

    Returns:
        dict: Updated room time slot availability matrix.
    """
    # Start with the basic availability
    room_time_slots = room_availability.copy()

    # Process room conflicts
    for room in rooms:
        if room["is_combined"] and room["component_rooms"]:
            room_id = room["room_id"]
            # For each time slot where this combined room is available
            for key in list(room_time_slots.keys()):
                r_id, day_idx, slot_idx = key
                if r_id == room_id and room_time_slots[key]:
                    # Find the component room IDs
                    component_ids = []
                    for component_name in room["component_rooms"]:
                        for r in rooms:
                            if r["room_name"] == component_name:
                                component_ids.append(r["room_id"])
                                break

                    # Mark this slot as unavailable for component rooms
                    for comp_id in component_ids:
                        room_time_slots[(comp_id, day_idx, slot_idx)] = False

    # Also handle the reverse - if a component room is in use, the combined room is unavailable
    for room in rooms:
        if not room["is_combined"]:
            room_id = room["room_id"]
            room_name = room["room_name"]

            # Find all combined rooms that include this room
            combined_room_ids = []
            for r in rooms:
                if (
                    r["is_combined"]
                    and r["component_rooms"]
                    and room_name in r["component_rooms"]
                ):
                    combined_room_ids.append(r["room_id"])

            # For each time slot where this room is available
            for key in list(room_time_slots.keys()):
                r_id, day_idx, slot_idx = key
                if r_id == room_id and room_time_slots[key]:
                    # Mark this slot as unavailable for combined rooms
                    for comb_id in combined_room_ids:
                        room_time_slots[(comb_id, day_idx, slot_idx)] = False

    return room_time_slots


def sort_classes_by_difficulty(classes, class_preferences):
    """
    Sort classes by scheduling difficulty.

    Args:
        classes (list): List of class data dictionaries.
        class_preferences (dict): Dictionary of class preferences.

    Returns:
        list: Sorted list of classes, hardest to schedule first.
    """
    class_scores = []

    for class_data in classes:
        class_id = class_data["class_id"]
        score = 0

        # Classes with longer duration are harder to schedule
        score += class_data["duration_slots"] * 10

        # Classes with specific preferences are harder to schedule
        if class_id in class_preferences:
            prefs = class_preferences[class_id]

            # Room preferences
            if "room" in prefs:
                # Fewer room options = higher score
                score += 50 / len(prefs["room"])
            else:
                # No room preference = easier to schedule
                score -= 20

            # Day preferences
            if "day" in prefs:
                # Fewer day options = higher score
                score += 30 / len(prefs["day"])
            else:
                # No day preference = easier to schedule
                score -= 15

            # Time preferences
            if "time" in prefs:
                # More time constraints = higher score
                score += len(prefs["time"]) * 5

        class_scores.append((score, class_id))

    # Sort by score descending (hardest first)
    class_scores.sort(reverse=True)

    # Return sorted classes
    sorted_classes = []
    for _, class_id in class_scores:
        for class_data in classes:
            if class_data["class_id"] == class_id:
                sorted_classes.append(class_data)
                break

    return sorted_classes


def find_compatible_slots(class_data, room_time_slots, rooms, class_preferences):
    """
    Find all compatible room-time slots for a class.

    Args:
        class_data (dict): Class data dictionary.
        room_time_slots (dict): Room time slot availability matrix.
        rooms (list): List of room data dictionaries.
        class_preferences (dict): Dictionary of class preferences.

    Returns:
        list: List of compatible (room_id, day_idx, start_slot) tuples.
    """
    compatible_slots = []
    class_id = class_data["class_id"]
    duration_slots = class_data["duration_slots"]

    # Get class preferences
    preferred_rooms = []
    preferred_days = []
    preferred_times = []

    if class_id in class_preferences:
        prefs = class_preferences[class_id]
        if "room" in prefs:
            preferred_rooms = [p["value"] for p in prefs["room"]]
        if "day" in prefs:
            preferred_days = [p["value"] for p in prefs["day"]]
        if "time" in prefs:
            preferred_times = [p["value"] for p in prefs["time"]]

    # Check all possible room-day-time combinations
    for room in rooms:
        room_id = room["room_id"]

        # Skip if room is not preferred (if preferences exist)
        if preferred_rooms and room_id not in preferred_rooms:
            continue

        for day_idx in range(7):
            # Skip if day is not preferred (if preferences exist)
            day_name = index_to_day(day_idx)
            if preferred_days and day_name not in preferred_days:
                continue

            for start_slot in range(96):  # 24 hours * 4 slots per hour
                # Skip if time is not preferred (if preferences exist)
                if preferred_times and start_slot not in preferred_times:
                    continue

                # Check if class fits in this slot
                fits = True
                for offset in range(duration_slots):
                    slot_key = (room_id, day_idx, start_slot + offset)
                    if not room_time_slots.get(slot_key, False):
                        fits = False
                        break

                if fits:
                    compatible_slots.append((room_id, day_idx, start_slot))

    return compatible_slots


def score_slot(slot, class_data, class_preferences, scheduled_classes, rooms):
    """
    Score a slot based on preferences and balance.

    Args:
        slot (tuple): (room_id, day_idx, start_slot) tuple.
        class_data (dict): Class data dictionary.
        class_preferences (dict): Dictionary of class preferences.
        scheduled_classes (list): List of already scheduled classes.
        rooms (list): List of room data dictionaries.

    Returns:
        float: Score for this slot.
    """
    room_id, day_idx, start_slot = slot
    class_id = class_data["class_id"]
    score = 0

    # Get class preferences
    if class_id in class_preferences:
        prefs = class_preferences[class_id]

        # Room preference score
        if "room" in prefs:
            for p in prefs["room"]:
                if p["value"] == room_id:
                    score += p["weight"] * 10
                    break

        # Day preference score
        if "day" in prefs:
            day_name = index_to_day(day_idx)
            for p in prefs["day"]:
                if p["value"] == day_name:
                    score += p["weight"] * 8
                    break

        # Time preference score
        if "time" in prefs:
            for p in prefs["time"]:
                time_slot = p["value"]
                if (
                    isinstance(time_slot, int)
                    and time_slot
                    <= start_slot
                    < time_slot + class_data["duration_slots"]
                ):
                    score += p["weight"] * 5
                    break

    # Room balance score
    room_counts = {}
    for r in rooms:
        room_counts[r["room_id"]] = 0

    for scheduled_class in scheduled_classes:
        if scheduled_class["room_id"] in room_counts:
            room_counts[scheduled_class["room_id"]] += 1

    # Prefer less utilized rooms
    current_room_count = room_counts.get(room_id, 0)
    max_room_count = max(room_counts.values()) if room_counts else 0
    if max_room_count > 0:
        score += (max_room_count - current_room_count) * 3

    # Day balance score
    day_counts = {d: 0 for d in range(7)}
    for scheduled_class in scheduled_classes:
        day_counts[scheduled_class["day_idx"]] += 1

    # Prefer less utilized days
    current_day_count = day_counts.get(day_idx, 0)
    max_day_count = max(day_counts.values()) if day_counts else 0
    if max_day_count > 0:
        score += (max_day_count - current_day_count) * 2

    # Time continuity score
    # Prefer slots adjacent to already scheduled classes of similar types
    for scheduled_class in scheduled_classes:
        if (
            scheduled_class["room_id"] == room_id
            and scheduled_class["day_idx"] == day_idx
        ):
            # Check if this class is right after the scheduled class
            if scheduled_class["end_slot"] == start_slot:
                # Bonus if same style
                if scheduled_class["style"] == class_data["style"]:
                    score += 5
                # Bonus if sequential levels
                if scheduled_class["level"] + 1 == class_data["level"]:
                    score += 3

            # Check if this class is right before the scheduled class
            if (
                start_slot + class_data["duration_slots"]
                == scheduled_class["start_slot"]
            ):
                # Bonus if same style
                if scheduled_class["style"] == class_data["style"]:
                    score += 5
                # Bonus if sequential levels
                if class_data["level"] + 1 == scheduled_class["level"]:
                    score += 3

    return score


def assign_classes_to_slots(classes, rooms, room_availability, class_preferences):
    """
    Assign classes to room-time slots.

    Args:
        classes (list): List of class data dictionaries.
        rooms (list): List of room data dictionaries.
        room_availability (dict): Dictionary mapping (room_id, day_idx, slot_idx) to availability.
        class_preferences (dict): Dictionary of class preferences.

    Returns:
        tuple: (scheduled_classes, unscheduled_classes) where each is a list of class dictionaries.
    """
    # Create room availability matrix
    room_time_slots = create_room_availability_matrix(rooms, room_availability)

    # Sort classes by difficulty
    sorted_classes = sort_classes_by_difficulty(classes, class_preferences)

    # Schedule each class
    scheduled_classes = []
    unscheduled_classes = []

    for class_data in sorted_classes:
        # Find all compatible slots
        compatible_slots = find_compatible_slots(
            class_data, room_time_slots, rooms, class_preferences
        )

        if compatible_slots:
            # Score each slot
            scored_slots = []
            for slot in compatible_slots:
                score = score_slot(
                    slot, class_data, class_preferences, scheduled_classes, rooms
                )
                scored_slots.append((score, slot))

            # Sort by score descending
            scored_slots.sort(reverse=True)

            # Select the best slot
            _, best_slot = scored_slots[0]
            room_id, day_idx, start_slot = best_slot

            # Schedule the class
            scheduled_class = {
                "class_id": class_data["class_id"],
                "class_name": class_data["class_name"],
                "style": class_data["style"],
                "level": class_data["level"],
                "age_start": class_data["age_start"],
                "age_end": class_data["age_end"],
                "duration": class_data["duration"],
                "duration_slots": class_data["duration_slots"],
                "room_id": room_id,
                "day_idx": day_idx,
                "day": index_to_day(day_idx),
                "start_slot": start_slot,
                "start_time": slot_index_to_time(start_slot),
                "end_slot": start_slot + class_data["duration_slots"],
                "end_time": slot_index_to_time(
                    start_slot + class_data["duration_slots"]
                ),
                "teacher_id": None,  # To be assigned in Phase 3
            }
            scheduled_classes.append(scheduled_class)

            # Update room availability
            for offset in range(class_data["duration_slots"]):
                slot_key = (room_id, day_idx, start_slot + offset)
                # Mark this slot as unavailable
                room_time_slots[slot_key] = False

                # Also mark conflicting rooms as unavailable
                for room in rooms:
                    # If this is a combined room, mark component rooms as unavailable
                    if (
                        room["room_id"] == room_id
                        and room["is_combined"]
                        and room["component_rooms"]
                    ):
                        for component_name in room["component_rooms"]:
                            for r in rooms:
                                if r["room_name"] == component_name:
                                    comp_key = (
                                        r["room_id"],
                                        day_idx,
                                        start_slot + offset,
                                    )
                                    room_time_slots[comp_key] = False

                    # If this is a component room, mark combined rooms as unavailable
                    for r in rooms:
                        if r["is_combined"] and r["component_rooms"]:
                            for component_name in r["component_rooms"]:
                                for comp_room in rooms:
                                    if (
                                        comp_room["room_name"] == component_name
                                        and comp_room["room_id"] == room_id
                                    ):
                                        comb_key = (
                                            r["room_id"],
                                            day_idx,
                                            start_slot + offset,
                                        )
                                        room_time_slots[comb_key] = False
        else:
            # No compatible slot found
            unscheduled_class = class_data.copy()
            unscheduled_class["reason"] = "No compatible room-time slot found"
            unscheduled_classes.append(unscheduled_class)

    return scheduled_classes, unscheduled_classes
