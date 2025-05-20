"""
Scheduler module for the Dance Studio Schedule Optimizer.

This module ties together the different phases of the scheduling approach.
"""

from data_loader import load_data
from output import create_schedule_output
from room_scheduler import assign_classes_to_slots
from teacher_scheduler import assign_teachers_to_classes
from visualization import create_schedule_visualization


def schedule_classes(data_file, output_dir="output", create_visuals=True):
    """
    Schedule classes using the phased approach.

    Args:
        data_file (str): Path to the Excel file containing schedule data.
        output_dir (str): Directory to save output files.
        create_visuals (bool): Whether to create schedule visualizations.

    Returns:
        tuple: (output_file_path, stats) where output_file_path is the path to
            the created output file and stats is a dictionary with statistics.
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
        data["teacher_names"],  # Pass teacher names mapping
    )

    # Calculate statistics
    classes = data["classes"]
    stats = {
        "total_classes": len(classes),
        "scheduled_classes": len(final_scheduled),
        "unscheduled_classes": len(all_unscheduled),
        "scheduling_rate": calc_scheduling_rate(final_scheduled, classes),
        "unscheduled_by_room": len(unscheduled_from_rooms),
        "unscheduled_by_teacher": len(unscheduled_from_teachers),
    }

    # Phase 5: Create visualization if requested
    if create_visuals:
        try:
            vis_file = create_schedule_visualization(output_file, output_dir)
            if vis_file:
                print(f"Schedule visualization created: {vis_file}")
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logging.warning(f"Could not create visualization due to {type(e).__name__}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during visualization: {type(e).__name__}: {e}")

    return output_file, stats


def calc_scheduling_rate(scheduled, all_classes):
    """
    Calculate the scheduling rate.

    Args:
        scheduled (list): List of scheduled classes.
        all_classes (list): List of all classes.

    Returns:
        float: Scheduling rate as a fraction.
    """
    if not all_classes:
        return 0
    return len(scheduled) / len(all_classes)
