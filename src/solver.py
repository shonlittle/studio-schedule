"""
Solver module for the Dance Studio Schedule Optimizer.

This module contains functions for solving the CP-SAT model and extracting
the solution.
"""

from ortools.sat.python import cp_model

from src.data_loader import index_to_day, time_slot_to_time


def solve_schedule(model, variables, classes, time_limit=60):
    """
    Solve the CP-SAT model and extract solution.

    Args:
        model (CpModel): The CP-SAT model.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.
        time_limit (int): Time limit for solving in seconds.

    Returns:
        tuple: (status, schedule) where status is a string indicating the
               solution status and schedule is a list of scheduled classes.
    """
    # Create CP-SAT solver
    solver = cp_model.CpSolver()

    # Set time limit
    solver.parameters.max_time_in_seconds = time_limit

    # Objective: Maximize the number of scheduled classes
    objective = model.NewIntVar(0, len(classes), "objective")
    model.Add(
        objective == sum(variables["class_scheduled"][i] for i in range(len(classes)))
    )
    model.Maximize(objective)

    # Solve the model
    status = solver.Solve(model)

    # Check if solution is feasible
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract solution
        schedule = extract_solution(solver, variables, classes)

        # Return status and schedule
        status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
        return status_str, schedule
    else:
        # No feasible solution found
        status_str = "INFEASIBLE" if status == cp_model.INFEASIBLE else "UNKNOWN"
        return status_str, []


def extract_solution(solver, variables, classes):
    """
    Extract solution from solver and convert to readable format.

    Args:
        solver (CpSolver): The CP-SAT solver.
        variables (dict): Dictionary of decision variables.
        classes (list): List of class data dictionaries.

    Returns:
        list: List of scheduled class dictionaries.
    """
    schedule = []

    # For each class
    for i, class_data in enumerate(classes):
        # Check if class is scheduled
        if solver.Value(variables["class_scheduled"][i]) == 1:
            # Get assigned values
            day_idx = solver.Value(variables["class_day"][i])
            start_slot = solver.Value(variables["class_start"][i])
            room_idx = solver.Value(variables["class_room"][i])
            teacher_idx = solver.Value(variables["class_teacher"][i])

            # Convert to readable format
            day = index_to_day(day_idx)
            start_time = time_slot_to_time(start_slot)
            end_time = time_slot_to_time(start_slot + class_data["duration_slots"])

            # Create scheduled class entry
            scheduled_class = {
                "class_name": class_data["class_name"],
                "style": class_data.get("style", ""),
                "level": class_data.get("level", ""),
                "age_range": f"{class_data.get('age_start', 0)}-{class_data.get('age_end', 99)}",
                "day": day,
                "start_time": start_time,
                "end_time": end_time,
                "room_idx": room_idx,
                "teacher_idx": teacher_idx,
                "duration": class_data["duration"],
            }

            schedule.append(scheduled_class)

    # Sort schedule by day and start time
    day_order = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    schedule.sort(key=lambda x: (day_order.get(x["day"], 7), x["start_time"]))

    return schedule


def get_solution_stats(schedule, classes, rooms, teachers):
    """
    Calculate statistics for the solution.

    Args:
        schedule (list): List of scheduled class dictionaries.
        classes (list): List of class data dictionaries.
        rooms (list): List of room data dictionaries.
        teachers (list): List of teacher data dictionaries.

    Returns:
        dict: Dictionary of solution statistics.
    """
    stats = {
        "total_classes": len(classes),
        "scheduled_classes": len(schedule),
        "scheduling_rate": len(schedule) / len(classes) if classes else 0,
        "room_utilization": {},
        "teacher_utilization": {},
    }

    # Calculate room utilization
    for room_idx, room in enumerate(rooms):
        room_name = room["room_name"]
        room_classes = [c for c in schedule if c["room_idx"] == room_idx]
        stats["room_utilization"][room_name] = len(room_classes)

    # Calculate teacher utilization
    for teacher_idx, teacher in enumerate(teachers):
        teacher_name = teacher["teacher_name"]
        teacher_classes = [c for c in schedule if c["teacher_idx"] == teacher_idx]
        stats["teacher_utilization"][teacher_name] = len(teacher_classes)

        # Calculate days worked
        days_worked = set(c["day"] for c in teacher_classes)
        stats["teacher_utilization"][f"{teacher_name}_days"] = len(days_worked)

    return stats
