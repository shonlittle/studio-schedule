"""
Scheduler module for the Dance Studio Schedule Optimizer.

This module ties together the different phases of the scheduling approach.
"""

from data_loader import load_data
from output import create_schedule_output
from room_scheduler import assign_classes_to_slots
from teacher_scheduler import assign_teachers_to_classes


def schedule_classes(data_file, output_dir="output"):
    """
    Schedule classes using the phased approach.

    Args:
        data_file (str): Path to the Excel file containing schedule data.
        output_dir (str): Directory to save output files.

    Returns:
        tuple: (output_file_path, stats) where output_file_path is the path to the
               created output file and stats is a dictionary with scheduling statistics.
    """
    # Load data
    data = load_data(data_file)

    # Phase 1 & 2: Assign classes to room-time slots
    scheduled_classes, unscheduled_from_rooms = assign_classes_to_slots(
        data["classes"],
        data["rooms"],
        data["room_availability"],
        data["class_preferences"],
    )

    # Phase 3: Assign teachers to scheduled classes
    final_scheduled, unscheduled_from_teachers = assign_teachers_to_classes(
        scheduled_classes,
        data["teacher_availability"],
        data["class_preferences"],
        data["teacher_specializations"],
    )

    # Combine unscheduled classes
    all_unscheduled = unscheduled_from_rooms + unscheduled_from_teachers

    # Phase 4: Generate output
    output_file = create_schedule_output(
        final_scheduled,
        all_unscheduled,
        data["rooms"],
        data["teacher_specializations"],
        output_dir,
    )

    # Calculate statistics
    stats = {
        "total_classes": len(data["classes"]),
        "scheduled_classes": len(final_scheduled),
        "unscheduled_classes": len(all_unscheduled),
        "scheduling_rate": (
            len(final_scheduled) / len(data["classes"]) if data["classes"] else 0
        ),
        "unscheduled_by_room": len(unscheduled_from_rooms),
        "unscheduled_by_teacher": len(unscheduled_from_teachers),
    }

    return output_file, stats
