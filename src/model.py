"""
Model module for the Dance Studio Schedule Optimizer.

This module contains functions for creating and configuring the CP-SAT model
with variables and constraints.
"""

from ortools.sat.python import cp_model

from data_loader import day_to_index, index_to_day


def create_model(
    classes, teachers, rooms, max_days=7, max_slots=24, relax_constraints=True
):
    """
    Create CP-SAT model with variables and constraints.

    Args:
        classes (list): List of class data dictionaries.
        teachers (list): List of teacher data dictionaries.
        rooms (list): List of room data dictionaries.
        max_days (int): Maximum number of days to consider.
        max_slots (int): Maximum number of time slots per day.

    Returns:
        tuple: (model, variables) where variables is a dictionary containing
               all decision variables.
    """
    # Initialize CP-SAT model
    model = cp_model.CpModel()

    # Create variables
    variables = {}

    # For each class, create variables for day, start time, room, and teacher
    variables["class_day"] = {}
    variables["class_start"] = {}
    variables["class_room"] = {}
    variables["class_teacher"] = {}

    # For tracking if a class is scheduled
    variables["class_scheduled"] = {}

    # For each class
    for i, class_data in enumerate(classes):
        # Day variable (0 = Monday, 1 = Tuesday, etc.)
        variables["class_day"][i] = model.NewIntVar(0, max_days - 1, f"class_{i}_day")

        # Start time slot variable
        variables["class_start"][i] = model.NewIntVar(
            0, max_slots - 1, f"class_{i}_start"
        )

        # Room variable (index into rooms list)
        variables["class_room"][i] = model.NewIntVar(
            0, len(rooms) - 1, f"class_{i}_room"
        )

        # Teacher variable (index into teachers list)
        variables["class_teacher"][i] = model.NewIntVar(
            0, len(teachers) - 1, f"class_{i}_teacher"
        )

        # Is class scheduled variable (1 if scheduled, 0 if not)
        variables["class_scheduled"][i] = model.NewBoolVar(f"class_{i}_scheduled")

    # Add constraints
    add_time_constraints(model, variables, classes, max_slots)
    add_room_constraints(model, variables, classes, rooms, relax_constraints)
    add_teacher_constraints(model, variables, classes, teachers, relax_constraints)
    add_preference_constraints(
        model, variables, classes, rooms, teachers, relax_constraints
    )

    return model, variables


def add_time_constraints(model, variables, classes, max_slots):
    """
    Add constraints related to time slots and durations.

    Args:
        model (CpModel): The CP-SAT model.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.
        max_slots (int): Maximum number of time slots per day.
    """
    # For each class
    for i, class_data in enumerate(classes):
        # Ensure class fits within available time slots
        # End time = start time + duration
        # End time must be <= max_slots
        model.Add(
            variables["class_start"][i] + class_data["duration_slots"] <= max_slots
        ).OnlyEnforceIf(variables["class_scheduled"][i])

        # If class is not scheduled, set day, start, room, and teacher to 0
        model.Add(variables["class_day"][i] == 0).OnlyEnforceIf(
            variables["class_scheduled"][i].Not()
        )
        model.Add(variables["class_start"][i] == 0).OnlyEnforceIf(
            variables["class_scheduled"][i].Not()
        )
        model.Add(variables["class_room"][i] == 0).OnlyEnforceIf(
            variables["class_scheduled"][i].Not()
        )
        model.Add(variables["class_teacher"][i] == 0).OnlyEnforceIf(
            variables["class_scheduled"][i].Not()
        )

    # Ensure classes don't overlap (same room, same day, overlapping time)
    for i, class_i in enumerate(classes):
        for j, class_j in enumerate(classes):
            if i < j:  # Only check each pair once
                # Classes overlap if:
                # 1. They are on the same day
                # 2. They are in the same room
                # 3. One starts during the other's time slot

                # Same day
                same_day = model.NewBoolVar(f"same_day_{i}_{j}")
                model.Add(
                    variables["class_day"][i] == variables["class_day"][j]
                ).OnlyEnforceIf(same_day)
                model.Add(
                    variables["class_day"][i] != variables["class_day"][j]
                ).OnlyEnforceIf(same_day.Not())

                # Same room
                same_room = model.NewBoolVar(f"same_room_{i}_{j}")
                model.Add(
                    variables["class_room"][i] == variables["class_room"][j]
                ).OnlyEnforceIf(same_room)
                model.Add(
                    variables["class_room"][i] != variables["class_room"][j]
                ).OnlyEnforceIf(same_room.Not())

                # Class i starts before class j ends
                i_before_j_ends = model.NewBoolVar(f"i_before_j_ends_{i}_{j}")
                model.Add(
                    variables["class_start"][i]
                    < variables["class_start"][j] + class_j["duration_slots"]
                ).OnlyEnforceIf(i_before_j_ends)
                model.Add(
                    variables["class_start"][i]
                    >= variables["class_start"][j] + class_j["duration_slots"]
                ).OnlyEnforceIf(i_before_j_ends.Not())

                # Class j starts before class i ends
                j_before_i_ends = model.NewBoolVar(f"j_before_i_ends_{i}_{j}")
                model.Add(
                    variables["class_start"][j]
                    < variables["class_start"][i] + class_i["duration_slots"]
                ).OnlyEnforceIf(j_before_i_ends)
                model.Add(
                    variables["class_start"][j]
                    >= variables["class_start"][i] + class_i["duration_slots"]
                ).OnlyEnforceIf(j_before_i_ends.Not())

                # Overlap occurs if same day, same room, and time overlap
                overlap = model.NewBoolVar(f"overlap_{i}_{j}")
                model.AddBoolAnd(
                    [same_day, same_room, i_before_j_ends, j_before_i_ends]
                ).OnlyEnforceIf(overlap)

                # Both classes must be scheduled for overlap to matter
                both_scheduled = model.NewBoolVar(f"both_scheduled_{i}_{j}")
                model.AddBoolAnd(
                    [variables["class_scheduled"][i], variables["class_scheduled"][j]]
                ).OnlyEnforceIf(both_scheduled)

                # If both are scheduled, they cannot overlap
                model.AddBoolAnd([both_scheduled, overlap.Not()])


def add_room_constraints(model, variables, classes, rooms, relax_constraints=True):
    """
    Add constraints related to rooms and room groups.

    Args:
        model (CpModel): The CP-SAT model.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.
        rooms (list): List of room data dictionaries.
    """
    # Create a mapping of room groups
    room_groups = {}
    for i, room in enumerate(rooms):
        group = room.get("group")
        if group:
            if group not in room_groups:
                room_groups[group] = []
            room_groups[group].append(i)

    # For each class
    for i, class_i in enumerate(classes):
        # Ensure class is assigned to a room that is available on the scheduled day
        for r, room in enumerate(rooms):
            # For each day
            for day_idx in range(7):
                day_name = index_to_day(day_idx)

                # If room is not available on this day
                if day_name not in room["availability"]:
                    if not relax_constraints:
                        # Class cannot be scheduled in this room on this day
                        room_day_conflict = model.NewBoolVar(
                            f"room_day_conflict_{i}_{r}_{day_idx}"
                        )
                        model.Add(variables["class_day"][i] == day_idx).OnlyEnforceIf(
                            room_day_conflict
                        )
                        model.Add(variables["class_room"][i] == r).OnlyEnforceIf(
                            room_day_conflict
                        )
                        model.AddBoolAnd(
                            [room_day_conflict, variables["class_scheduled"][i].Not()]
                        )

                # If room is available on this day, check time slots
                else:
                    available_slots = room["availability"][day_name]

                    # For each possible start time
                    for start_slot in range(24):  # Assuming max 24 slots
                        # Check if class fits within available slots
                        fits = True
                        for slot_offset in range(class_i["duration_slots"]):
                            if start_slot + slot_offset not in available_slots:
                                fits = False
                                break

                        if not fits:
                            # Class cannot start at this time in this room on this day
                            conflict = model.NewBoolVar(
                                f"conflict_{i}_{r}_{day_idx}_{start_slot}"
                            )
                            model.Add(
                                variables["class_day"][i] == day_idx
                            ).OnlyEnforceIf(conflict)
                            model.Add(variables["class_room"][i] == r).OnlyEnforceIf(
                                conflict
                            )
                            model.Add(
                                variables["class_start"][i] == start_slot
                            ).OnlyEnforceIf(conflict)
                            model.AddBoolAnd(
                                [conflict, variables["class_scheduled"][i].Not()]
                            )

    # Enforce room group exclusivity
    for group, room_indices in room_groups.items():
        # For each pair of rooms in the same group
        for i, room_i in enumerate(room_indices):
            for j, room_j in enumerate(room_indices):
                if i < j:  # Only check each pair once
                    # For each pair of classes
                    for c1, class_1 in enumerate(classes):
                        for c2, class_2 in enumerate(classes):
                            if c1 < c2:  # Only check each pair once
                                # If classes are on the same day and in rooms of the same group
                                # they cannot overlap in time

                                # Same day
                                same_day = model.NewBoolVar(f"group_same_day_{c1}_{c2}")
                                model.Add(
                                    variables["class_day"][c1]
                                    == variables["class_day"][c2]
                                ).OnlyEnforceIf(same_day)
                                model.Add(
                                    variables["class_day"][c1]
                                    != variables["class_day"][c2]
                                ).OnlyEnforceIf(same_day.Not())

                                # Class 1 in room i of group
                                c1_in_room_i = model.NewBoolVar(
                                    f"c1_in_room_i_{c1}_{room_i}"
                                )
                                model.Add(
                                    variables["class_room"][c1] == room_i
                                ).OnlyEnforceIf(c1_in_room_i)
                                model.Add(
                                    variables["class_room"][c1] != room_i
                                ).OnlyEnforceIf(c1_in_room_i.Not())

                                # Class 2 in room j of group
                                c2_in_room_j = model.NewBoolVar(
                                    f"c2_in_room_j_{c2}_{room_j}"
                                )
                                model.Add(
                                    variables["class_room"][c2] == room_j
                                ).OnlyEnforceIf(c2_in_room_j)
                                model.Add(
                                    variables["class_room"][c2] != room_j
                                ).OnlyEnforceIf(c2_in_room_j.Not())

                                # Time overlap check (similar to room overlap check)
                                # Class 1 starts before class 2 ends
                                c1_before_c2_ends = model.NewBoolVar(
                                    f"c1_before_c2_ends_{c1}_{c2}"
                                )
                                model.Add(
                                    variables["class_start"][c1]
                                    < variables["class_start"][c2]
                                    + class_2["duration_slots"]
                                ).OnlyEnforceIf(c1_before_c2_ends)
                                model.Add(
                                    variables["class_start"][c1]
                                    >= variables["class_start"][c2]
                                    + class_2["duration_slots"]
                                ).OnlyEnforceIf(c1_before_c2_ends.Not())

                                # Class 2 starts before class 1 ends
                                c2_before_c1_ends = model.NewBoolVar(
                                    f"c2_before_c1_ends_{c1}_{c2}"
                                )
                                model.Add(
                                    variables["class_start"][c2]
                                    < variables["class_start"][c1]
                                    + class_1["duration_slots"]
                                ).OnlyEnforceIf(c2_before_c1_ends)
                                model.Add(
                                    variables["class_start"][c2]
                                    >= variables["class_start"][c1]
                                    + class_1["duration_slots"]
                                ).OnlyEnforceIf(c2_before_c1_ends.Not())

                                # Time overlap occurs
                                time_overlap = model.NewBoolVar(
                                    f"group_time_overlap_{c1}_{c2}"
                                )
                                model.AddBoolAnd(
                                    [c1_before_c2_ends, c2_before_c1_ends]
                                ).OnlyEnforceIf(time_overlap)

                                # Group conflict occurs if:
                                # 1. Same day
                                # 2. Class 1 in room i of group
                                # 3. Class 2 in room j of group
                                # 4. Time overlap
                                group_conflict = model.NewBoolVar(
                                    f"group_conflict_{c1}_{c2}_{room_i}_{room_j}"
                                )
                                model.AddBoolAnd(
                                    [same_day, c1_in_room_i, c2_in_room_j, time_overlap]
                                ).OnlyEnforceIf(group_conflict)

                                # Both classes must be scheduled for conflict to matter
                                both_scheduled = model.NewBoolVar(
                                    f"group_both_scheduled_{c1}_{c2}"
                                )
                                model.AddBoolAnd(
                                    [
                                        variables["class_scheduled"][c1],
                                        variables["class_scheduled"][c2],
                                    ]
                                ).OnlyEnforceIf(both_scheduled)

                                # If both are scheduled, they cannot have a group conflict
                                model.AddBoolAnd([both_scheduled, group_conflict.Not()])


def add_teacher_constraints(
    model, variables, classes, teachers, relax_constraints=True
):
    """
    Add constraints related to teachers.

    Args:
        model (CpModel): The CP-SAT model.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.
        teachers (list): List of teacher data dictionaries.
    """
    # For each class
    for i, class_i in enumerate(classes):
        # Ensure class is assigned to a teacher that is available on the scheduled day
        for t, teacher in enumerate(teachers):
            # For each day
            for day_idx in range(7):
                day_name = index_to_day(day_idx)

                # If teacher is not available on this day
                if day_name not in teacher["availability"]:
                    if not relax_constraints:
                        # Class cannot be scheduled with this teacher on this day
                        teacher_day_conflict = model.NewBoolVar(
                            f"teacher_day_conflict_{i}_{t}_{day_idx}"
                        )
                        model.Add(variables["class_day"][i] == day_idx).OnlyEnforceIf(
                            teacher_day_conflict
                        )
                        model.Add(variables["class_teacher"][i] == t).OnlyEnforceIf(
                            teacher_day_conflict
                        )
                        model.AddBoolAnd(
                            [
                                teacher_day_conflict,
                                variables["class_scheduled"][i].Not(),
                            ]
                        )

                # If teacher is available on this day, check time slots
                else:
                    available_slots = teacher["availability"][day_name]

                    # For each possible start time
                    for start_slot in range(24):  # Assuming max 24 slots
                        # Check if class fits within available slots
                        fits = True
                        for slot_offset in range(class_i["duration_slots"]):
                            if start_slot + slot_offset not in available_slots:
                                fits = False
                                break

                        if not fits and not relax_constraints:
                            # Class cannot start at this time with this teacher on this day
                            conflict = model.NewBoolVar(
                                f"teacher_conflict_{i}_{t}_{day_idx}_{start_slot}"
                            )
                            model.Add(
                                variables["class_day"][i] == day_idx
                            ).OnlyEnforceIf(conflict)
                            model.Add(variables["class_teacher"][i] == t).OnlyEnforceIf(
                                conflict
                            )
                            model.Add(
                                variables["class_start"][i] == start_slot
                            ).OnlyEnforceIf(conflict)
                            model.AddBoolAnd(
                                [conflict, variables["class_scheduled"][i].Not()]
                            )

    # Ensure teachers aren't double-booked
    for i, class_i in enumerate(classes):
        for j, class_j in enumerate(classes):
            if i < j:  # Only check each pair once
                # Same day
                same_day = model.NewBoolVar(f"teacher_same_day_{i}_{j}")
                model.Add(
                    variables["class_day"][i] == variables["class_day"][j]
                ).OnlyEnforceIf(same_day)
                model.Add(
                    variables["class_day"][i] != variables["class_day"][j]
                ).OnlyEnforceIf(same_day.Not())

                # Same teacher
                same_teacher = model.NewBoolVar(f"same_teacher_{i}_{j}")
                model.Add(
                    variables["class_teacher"][i] == variables["class_teacher"][j]
                ).OnlyEnforceIf(same_teacher)
                model.Add(
                    variables["class_teacher"][i] != variables["class_teacher"][j]
                ).OnlyEnforceIf(same_teacher.Not())

                # Time overlap check
                # Class i starts before class j ends
                i_before_j_ends = model.NewBoolVar(f"teacher_i_before_j_ends_{i}_{j}")
                model.Add(
                    variables["class_start"][i]
                    < variables["class_start"][j] + class_j["duration_slots"]
                ).OnlyEnforceIf(i_before_j_ends)
                model.Add(
                    variables["class_start"][i]
                    >= variables["class_start"][j] + class_j["duration_slots"]
                ).OnlyEnforceIf(i_before_j_ends.Not())

                # Class j starts before class i ends
                j_before_i_ends = model.NewBoolVar(f"teacher_j_before_i_ends_{i}_{j}")
                model.Add(
                    variables["class_start"][j]
                    < variables["class_start"][i] + class_i["duration_slots"]
                ).OnlyEnforceIf(j_before_i_ends)
                model.Add(
                    variables["class_start"][j]
                    >= variables["class_start"][i] + class_i["duration_slots"]
                ).OnlyEnforceIf(j_before_i_ends.Not())

                # Time overlap occurs
                time_overlap = model.NewBoolVar(f"teacher_time_overlap_{i}_{j}")
                model.AddBoolAnd([i_before_j_ends, j_before_i_ends]).OnlyEnforceIf(
                    time_overlap
                )

                # Teacher conflict occurs if:
                # 1. Same day
                # 2. Same teacher
                # 3. Time overlap
                teacher_conflict = model.NewBoolVar(f"teacher_conflict_{i}_{j}")
                model.AddBoolAnd([same_day, same_teacher, time_overlap]).OnlyEnforceIf(
                    teacher_conflict
                )

                # Both classes must be scheduled for conflict to matter
                both_scheduled = model.NewBoolVar(f"teacher_both_scheduled_{i}_{j}")
                model.AddBoolAnd(
                    [variables["class_scheduled"][i], variables["class_scheduled"][j]]
                ).OnlyEnforceIf(both_scheduled)

                # If both are scheduled, they cannot have a teacher conflict
                model.AddBoolAnd([both_scheduled, teacher_conflict.Not()])

    # Add constraints to balance teacher workload
    # Apply these constraints regardless of relax_constraints setting
    # Create variables to track if a class is assigned to a teacher
    teacher_class_vars = {}
    for t in range(len(teachers)):
        teacher_class_vars[t] = {}
        for i in range(len(classes)):
            # Create a boolean variable that is true if class i is assigned to teacher t
            class_has_teacher_t = model.NewBoolVar(f"class_{i}_has_teacher_{t}")

            # This variable is true if class i is scheduled with teacher t
            model.Add(variables["class_teacher"][i] == t).OnlyEnforceIf(
                class_has_teacher_t
            )
            model.Add(variables["class_teacher"][i] != t).OnlyEnforceIf(
                class_has_teacher_t.Not()
            )

            # This variable is true if class i is scheduled with teacher t
            teacher_class_vars[t][i] = model.NewBoolVar(
                f"teacher_{t}_class_{i}_scheduled"
            )

            # Link the variables: teacher_class_vars[t][i] is true if class i is scheduled AND has teacher t
            model.AddBoolAnd(
                [variables["class_scheduled"][i], class_has_teacher_t]
            ).OnlyEnforceIf(teacher_class_vars[t][i])

            # If either class is not scheduled or doesn't have teacher t, then teacher_class_vars[t][i] is false
            not_scheduled_or_not_teacher_t = model.NewBoolVar(
                f"not_scheduled_or_not_teacher_{t}_{i}"
            )
            model.AddBoolOr(
                [variables["class_scheduled"][i].Not(), class_has_teacher_t.Not()]
            ).OnlyEnforceIf(not_scheduled_or_not_teacher_t)
            model.AddImplication(
                not_scheduled_or_not_teacher_t, teacher_class_vars[t][i].Not()
            )

        # Count classes per teacher
        teacher_class_count = model.NewIntVar(0, len(classes), f"teacher_{t}_classes")
        model.Add(teacher_class_count == sum(teacher_class_vars[t].values()))

        # Limit classes per teacher (adjust max_classes_per_teacher as needed)
        max_classes_per_teacher = 20  # Adjust this value based on your requirements
        model.Add(teacher_class_count <= max_classes_per_teacher)

        # Ensure each teacher has at least some classes (if there are enough classes)
        min_classes_per_teacher = 1  # Adjust this value based on your requirements
        if len(classes) >= len(teachers) * min_classes_per_teacher:
            model.Add(teacher_class_count >= min_classes_per_teacher)

    # Add constraints to distribute classes across days
    for day_idx in range(7):
        # Create variables to track if a class is scheduled on this day
        day_class_vars = []
        for i in range(len(classes)):
            # Create a boolean variable that is true if class i is scheduled on day_idx
            day_class_var = model.NewBoolVar(f"day_{day_idx}_class_{i}")

            # Create a boolean variable that is true if class i is assigned to day_idx
            class_has_day = model.NewBoolVar(f"class_{i}_has_day_{day_idx}")

            # This variable is true if class i is scheduled on day_idx
            model.Add(variables["class_day"][i] == day_idx).OnlyEnforceIf(class_has_day)
            model.Add(variables["class_day"][i] != day_idx).OnlyEnforceIf(
                class_has_day.Not()
            )

            # Link the variables: day_class_var is true if class i is scheduled AND has day_idx
            model.AddBoolAnd(
                [variables["class_scheduled"][i], class_has_day]
            ).OnlyEnforceIf(day_class_var)

            # If either class is not scheduled or doesn't have day_idx, then day_class_var is false
            not_scheduled_or_not_day = model.NewBoolVar(
                f"not_scheduled_or_not_day_{day_idx}_{i}"
            )
            model.AddBoolOr(
                [variables["class_scheduled"][i].Not(), class_has_day.Not()]
            ).OnlyEnforceIf(not_scheduled_or_not_day)
            model.AddImplication(not_scheduled_or_not_day, day_class_var.Not())

            day_class_vars.append(day_class_var)

        # Count classes per day
        day_class_count = model.NewIntVar(0, len(classes), f"day_{day_idx}_classes")
        model.Add(day_class_count == sum(day_class_vars))

        # Limit classes per day (adjust max_classes_per_day as needed)
        max_classes_per_day = 30  # Adjust this value based on your requirements
        model.Add(day_class_count <= max_classes_per_day)


def add_preference_constraints(
    model, variables, classes, rooms, teachers, relax_constraints=True
):
    """
    Add constraints related to preferences.

    Args:
        model (CpModel): The CP-SAT model.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.
    """
    # For each class
    for i, class_data in enumerate(classes):
        # Preferred days
        if class_data["preferred_days"]:
            # Create a list of allowed day indices
            allowed_days = [day_to_index(day) for day in class_data["preferred_days"]]

            # Class must be scheduled on one of the preferred days
            if not relax_constraints:
                for day_idx in range(7):
                    if day_idx not in allowed_days:
                        # If day is not in allowed days, class cannot be scheduled on this day
                        not_allowed_day = model.NewBoolVar(
                            f"not_allowed_day_{i}_{day_idx}"
                        )
                        model.Add(variables["class_day"][i] == day_idx).OnlyEnforceIf(
                            not_allowed_day
                        )
                        model.AddBoolAnd(
                            [not_allowed_day, variables["class_scheduled"][i].Not()]
                        )

        # Preferred time ranges
        if class_data["preferred_time_ranges"]:
            # For each day
            for day_name, time_slots in class_data["preferred_time_ranges"].items():
                day_idx = day_to_index(day_name)

                # If class is scheduled on this day
                day_match = model.NewBoolVar(f"day_match_{i}_{day_idx}")
                model.Add(variables["class_day"][i] == day_idx).OnlyEnforceIf(day_match)
                model.Add(variables["class_day"][i] != day_idx).OnlyEnforceIf(
                    day_match.Not()
                )

                # If time slots are specified for this day
                if time_slots:
                    # Class must start at one of the allowed start times
                    # We need to account for class duration
                    allowed_starts = []
                    for slot in time_slots:
                        # Check if class can fit if it starts at this slot
                        can_fit = True
                        for offset in range(class_data["duration_slots"]):
                            if slot + offset not in time_slots:
                                can_fit = False
                                break

                        if can_fit:
                            allowed_starts.append(slot)

                    # If there are allowed start times
                    if allowed_starts:
                        # Class must start at one of the allowed times if scheduled on this day
                        time_constraint = model.NewBoolVar(
                            f"time_constraint_{i}_{day_idx}"
                        )
                        # For each possible start time
                        for start_slot in range(24):  # Assuming max 24 slots
                            if start_slot not in allowed_starts:
                                # If start time is not allowed, class cannot start at this time
                                not_allowed_start = model.NewBoolVar(
                                    f"not_allowed_start_{i}_{day_idx}_{start_slot}"
                                )
                                model.Add(
                                    variables["class_start"][i] == start_slot
                                ).OnlyEnforceIf(not_allowed_start)
                                model.AddBoolAnd(
                                    [not_allowed_start, time_constraint.Not()]
                                )

                        if relax_constraints:
                            # If relax_constraints is True, time preferences are optional
                            # We'll add a soft constraint by not enforcing it
                            pass
                        else:
                            # If relax_constraints is False, time preferences are required
                            # If class is scheduled on this day, time constraint must be satisfied
                            model.AddBoolAnd(
                                [day_match, time_constraint]
                            ).OnlyEnforceIf(variables["class_scheduled"][i])

        # Preferred rooms
        if class_data["preferred_rooms"]:
            # Create a list of allowed room indices
            allowed_rooms = []
            for room_name in class_data["preferred_rooms"]:
                for r, room in enumerate(rooms):
                    if room["room_name"] == room_name:
                        allowed_rooms.append(r)
                        break

            # Class must be scheduled in one of the preferred rooms
            if not relax_constraints and allowed_rooms:
                for r in range(len(rooms)):
                    if r not in allowed_rooms:
                        # If room is not in allowed rooms, class cannot be scheduled in this room
                        not_allowed_room = model.NewBoolVar(f"not_allowed_room_{i}_{r}")
                        model.Add(variables["class_room"][i] == r).OnlyEnforceIf(
                            not_allowed_room
                        )
                        model.AddBoolAnd(
                            [not_allowed_room, variables["class_scheduled"][i].Not()]
                        )

        # Preferred teachers
        if class_data["preferred_teachers"]:
            # Create a list of allowed teacher indices
            allowed_teachers = []
            for teacher_name in class_data["preferred_teachers"]:
                for t, teacher in enumerate(teachers):
                    if teacher["teacher_name"] == teacher_name:
                        allowed_teachers.append(t)
                        break

            # Class must be scheduled with one of the preferred teachers
            if not relax_constraints and allowed_teachers:
                for t in range(len(teachers)):
                    if t not in allowed_teachers:
                        # If teacher is not in allowed teachers, class cannot be scheduled with this teacher
                        not_allowed_teacher = model.NewBoolVar(
                            f"not_allowed_teacher_{i}_{t}"
                        )
                        model.Add(variables["class_teacher"][i] == t).OnlyEnforceIf(
                            not_allowed_teacher
                        )
                        model.AddBoolAnd(
                            [not_allowed_teacher, variables["class_scheduled"][i].Not()]
                        )
