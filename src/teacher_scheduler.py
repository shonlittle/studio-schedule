"""
Teacher scheduler module for the Dance Studio Schedule Optimizer.

This module contains functions for assigning teachers to scheduled classes
(Phase 3).
"""


def assign_teachers_to_classes(
    scheduled_classes,
    teacher_availability,
    class_preferences,
    teacher_specializations,
):
    """
    Assign teachers to scheduled classes.

    Args:
        scheduled_classes (list): List of scheduled class dictionaries.
        teacher_availability (dict): Dictionary mapping
            (teacher_id, day_idx, slot_idx) to availability.
        class_preferences (dict): Dictionary of class preferences.
        teacher_specializations (dict): Dictionary of teacher specializations.

    Returns:
        tuple: (assigned_classes, unassigned_classes) where each is a list
            of class dictionaries.
    """
    # Sort classes chronologically
    scheduled_classes.sort(key=lambda c: (c["day_idx"], c["start_slot"]))

    # Create a copy of teacher availability
    teacher_avail = teacher_availability.copy()

    # For each class
    for scheduled_class in scheduled_classes:
        class_id = scheduled_class["class_id"]
        day_idx = scheduled_class["day_idx"]
        start_slot = scheduled_class["start_slot"]
        end_slot = scheduled_class["end_slot"]

        # Find preferred teachers
        preferred_teachers = []
        has_prefs = class_id in class_preferences
        if has_prefs and "teacher" in class_preferences[class_id]:
            preferred_teachers = [
                (p["value"], p["weight"])
                for p in class_preferences[class_id]["teacher"]
            ]

        # Find all available teachers
        available_teachers = []
        for teacher_id in teacher_specializations.keys():
            # Check if teacher is available for the entire class duration
            is_available = True
            for slot in range(start_slot, end_slot):
                if not teacher_avail.get((teacher_id, day_idx, slot), False):
                    is_available = False
                    break

            if is_available:
                # Score this teacher
                score = score_teacher(
                    teacher_id,
                    scheduled_class,
                    preferred_teachers,
                    teacher_specializations,
                )
                available_teachers.append((score, teacher_id))

        if available_teachers:
            # Sort by score descending
            available_teachers.sort(reverse=True)

            # Select the best teacher
            _, best_teacher = available_teachers[0]

            # Assign teacher to class
            scheduled_class["teacher_id"] = best_teacher

            # Update teacher availability
            for slot in range(start_slot, end_slot):
                teacher_avail[(best_teacher, day_idx, slot)] = False

    # Identify classes without teachers
    unassigned_classes = []
    assigned_classes = []

    for scheduled_class in scheduled_classes:
        if scheduled_class["teacher_id"] is None:
            unassigned_class = scheduled_class.copy()
            unassigned_class["reason"] = "No available teacher found"
            unassigned_classes.append(unassigned_class)
        else:
            assigned_classes.append(scheduled_class)

    return assigned_classes, unassigned_classes


def score_teacher(
    teacher_id, scheduled_class, preferred_teachers, teacher_specializations
):
    """
    Score a teacher for a class based on preferences and specialization.

    Args:
        teacher_id (int): Teacher ID.
        scheduled_class (dict): Scheduled class dictionary.
        preferred_teachers (list): List of (teacher_id, weight) tuples.
        teacher_specializations (dict): Dictionary of teacher specializations.

    Returns:
        float: Score for this teacher.
    """
    score = 0

    # Preference score
    for teacher, weight in preferred_teachers:
        if teacher == teacher_id:
            score += weight * 10
            break

    # Specialization score
    if teacher_id in teacher_specializations:
        specializations = teacher_specializations[teacher_id]

        # Style match
        if (
            "style" in specializations
            and scheduled_class["style"] in specializations["style"]
        ):
            score += 8

        # Age group match
        if "age_group" in specializations:
            for age_group in specializations["age_group"]:
                # Parse age range (e.g., "7-18")
                try:
                    age_start, age_end = map(int, age_group.split("-"))
                    if (
                        scheduled_class["age_start"] >= age_start
                        and scheduled_class["age_end"] <= age_end
                    ):
                        score += 5
                        break
                except (ValueError, IndexError):
                    # If parsing fails, just check for exact match
                    start = scheduled_class["age_start"]
                    end = scheduled_class["age_end"]
                    age_range = f"{start}-{end}"
                    if age_group == age_range:
                        score += 5
                        break

        # Level match
        if "level" in specializations:
            level_str = str(scheduled_class["level"])
            if level_str in specializations["level"]:
                score += 3

    return score
