"""
Visualization module for the Dance Studio Schedule Optimizer.

This module contains functions for creating visual representations of the
schedule, including a weekly schedule visualization with classes mapped by
room and time.
"""

import os
from datetime import datetime

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_schedule_visualization(schedule_file, output_dir="output", save_pdf=False):
    """
    Create a visual representation of the schedule.

    Args:
        schedule_file (str): Path to the Excel schedule file.
        output_dir (str): Directory to save the visualization.
        save_pdf (bool): Whether to also save as PDF.

    Returns:
        str: Path to the created visualization file.
    """
    # Read the Excel file
    schedule_df = pd.read_excel(schedule_file, sheet_name="Schedule")

    # Process the data for visualization
    days_data = process_schedule_data(schedule_df)

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(schedule_file))[0]

    # Create the visualization
    fig_path = create_weekly_visualization(
        days_data, output_dir, base_filename, save_pdf
    )

    return fig_path


def process_schedule_data(schedule_df):
    """
    Process the schedule data for visualization.

    Args:
        schedule_df (DataFrame): DataFrame with schedule information.

    Returns:
        dict: Dictionary with processed data for each day.
    """
    # Define day order
    day_order = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    # Initialize data structure for each day
    days_data = {day: [] for day in day_order}

    # Process each class
    for _, row in schedule_df.iterrows():
        day = row["Day"]

        # Skip if day is not in our day order (shouldn't happen, but just in case)
        if day not in day_order:
            continue

        # Parse start and end times
        start_time = datetime.strptime(row["Start Time"], "%H:%M")
        end_time = datetime.strptime(row["End Time"], "%H:%M")

        # Calculate duration in hours (for block height)
        duration = (end_time - start_time).total_seconds() / 3600

        # Handle combined rooms
        room = row["Room"]
        rooms_to_use = []

        # Check if this is a combined room (contains '+')
        if "+" in room:
            # Handle specific combined room patterns directly
            if "Room 1+2" in room:
                rooms_to_use = [1, 2]
            elif "Room 3+4" in room:
                rooms_to_use = [3, 4]
            else:
                # Split the combined room into individual rooms
                room_parts = room.split("+")
                for part in room_parts:
                    # Clean up room name and extract room number
                    clean_part = part.strip()
                    if "Room" in clean_part:
                        # Extract room number using more robust method
                        # Remove "Room" and any non-digit characters
                        room_str = "".join(
                            c for c in clean_part.replace("Room", "") if c.isdigit()
                        )
                        if room_str:
                            room_num = int(room_str)
                            rooms_to_use.append(room_num)

            # Combined room successfully processed
        else:
            # Single room, extract room number
            if "Room" in room:
                # Extract room number using more robust method
                room_str = "".join(c for c in room.replace("Room", "") if c.isdigit())
                if room_str:
                    room_num = int(room_str)
                    rooms_to_use.append(room_num)

        # Create class data
        class_data = {
            "class_name": row["Class Name"],
            "teacher_name": row["Teacher Name"],
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "rooms": rooms_to_use,
            "is_combined": len(rooms_to_use) > 1,
            "original_room": room,  # Store the original room string
        }

        # Add to the appropriate day
        days_data[day].append(class_data)

    return days_data


def create_weekly_visualization(days_data, output_dir, base_filename, save_pdf=False):
    """
    Create a weekly visualization of the schedule.

    Args:
        days_data (dict): Dictionary with processed data for each day.
        output_dir (str): Directory to save the visualization.
        base_filename (str): Base filename for the output file.
        save_pdf (bool): Whether to also save as PDF.

    Returns:
        str: Path to the created visualization file.
    """
    # Define day order
    day_order = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    # Filter out days with no classes
    active_days = [day for day in day_order if days_data[day]]

    # If no days have classes, return early
    if not active_days:
        print("No classes found in the schedule.")
        return None

    # Determine time range across all days
    all_classes = []
    for day in active_days:
        all_classes.extend(days_data[day])

    # Find earliest start time and latest end time
    if all_classes:
        earliest_start = min(c["start_time"] for c in all_classes)
        latest_end = max(c["end_time"] for c in all_classes)
    else:
        # Default time range if no classes
        earliest_start = datetime.strptime("08:00", "%H:%M")
        latest_end = datetime.strptime("20:00", "%H:%M")

    # Round to nearest 15 minutes for clean display
    earliest_hour = earliest_start.hour
    earliest_minute = (earliest_start.minute // 15) * 15
    earliest_start = datetime.strptime(
        f"{earliest_hour:02d}:{earliest_minute:02d}", "%H:%M"
    )

    latest_hour = latest_end.hour
    latest_minute = ((latest_end.minute + 14) // 15) * 15  # Round up
    if latest_minute == 60:
        latest_hour += 1
        latest_minute = 0
    latest_end = datetime.strptime(f"{latest_hour:02d}:{latest_minute:02d}", "%H:%M")

    # Process each day independently
    day_time_points = {}
    day_time_to_position = {}
    day_num_positions = {}

    # Calculate time points and positions for each day separately
    for day in active_days:
        # Collect time points for this day only
        time_points = set()
        for class_data in days_data[day]:
            time_points.add(class_data["start_time"])
            time_points.add(class_data["end_time"])

        # Sort time points for this day
        sorted_time_points = sorted(time_points)

        # Create day-specific mapping
        day_time_points[day] = sorted_time_points
        day_time_to_position[day] = {
            time: i for i, time in enumerate(sorted_time_points)
        }
        day_num_positions[day] = len(sorted_time_points)

    # Calculate height ratios based on number of time positions per day
    height_ratios = [day_num_positions[day] for day in active_days]

    # Create figure with subplots for each day
    # Base height on the sum of all day positions
    total_positions = sum(height_ratios)
    fig_height = 2 + (total_positions * 0.4)  # Adjust scaling factor
    fig_width = 12  # Fixed width

    fig, axes = plt.subplots(
        len(active_days),
        1,
        figsize=(fig_width, fig_height),
        gridspec_kw={"height_ratios": height_ratios},
    )

    # Handle case with only one day
    if len(active_days) == 1:
        axes = [axes]

    # Collect all unique teacher names across all days
    all_teachers = set()
    for day in active_days:
        for class_data in days_data[day]:
            all_teachers.add(class_data["teacher_name"])

    # Sort teacher names for consistent color assignment
    sorted_teachers = sorted(list(all_teachers))

    # Choose an appropriate colormap with enough colors for all teachers
    num_teachers = len(sorted_teachers)
    if num_teachers <= 10:
        cmap = plt.cm.get_cmap("tab10", 10)
    elif num_teachers <= 20:
        cmap = plt.cm.get_cmap("tab20", 20)
    else:
        # For more than 20 teachers, use a continuous colormap
        cmap = plt.cm.get_cmap("hsv", num_teachers)

    # Create a mapping of teacher names to colors
    teacher_colors = {
        teacher: cmap(i % num_teachers) for i, teacher in enumerate(sorted_teachers)
    }

    # Process each day
    for i, day in enumerate(active_days):
        ax = axes[i]

        # Get day-specific data
        day_sorted_time_points = day_time_points[day]
        day_position_map = day_time_to_position[day]
        day_position_count = day_num_positions[day]

        # Set up the grid
        ax.set_xlim(0, 4)  # 4 rooms
        ax.set_ylim(0, day_position_count - 1)  # Day-specific y-axis limits

        # Add room labels on x-axis
        ax.set_xticks([0.5, 1.5, 2.5, 3.5])
        ax.set_xticklabels(["Room 1", "Room 2", "Room 3", "Room 4"])

        # Add time labels on y-axis - day specific
        y_ticks = np.arange(0, day_position_count)  # All time points for this day
        y_labels = [day_sorted_time_points[i].strftime("%H:%M") for i in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

        # Invert y-axis so time flows downward
        ax.invert_yaxis()

        # Add day label
        ax.set_title(day, fontsize=14, fontweight="bold")

        # Add grid lines
        ax.grid(True, linestyle="--", alpha=0.7)

        # Plot classes for this day
        for j, class_data in enumerate(days_data[day]):
            # Calculate position using the day-specific time mapping
            start_pos = day_position_map[class_data["start_time"]]
            end_pos = day_position_map[class_data["end_time"]]
            height = end_pos - start_pos

            # Get color for this class based on teacher name
            color = teacher_colors[class_data["teacher_name"]]

            # Handle combined rooms
            if class_data["is_combined"]:
                # Check for specific combined room patterns
                original_room = class_data["original_room"]

                # Process combined room

                # Handle Room 1+2
                if "1+2" in original_room or (
                    1 in class_data["rooms"] and 2 in class_data["rooms"]
                ):
                    # Create rectangle spanning Room 1 and Room 2
                    rect = patches.Rectangle(
                        (0, start_pos),  # Start at Room 1 (index 0)
                        2,  # Span 2 rooms
                        height,
                        linewidth=1,
                        edgecolor="black",
                        facecolor=color,
                        alpha=0.7,
                    )
                    ax.add_patch(rect)

                    # Add class name and teacher name in the middle of the rectangle
                    ax.text(
                        1,  # Center between Room 1 and Room 2
                        start_pos + height / 2,
                        f"{class_data['class_name']}\n{class_data['teacher_name']}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"
                        ),
                    )

                # Handle Room 3+4
                elif "3+4" in original_room or (
                    3 in class_data["rooms"] and 4 in class_data["rooms"]
                ):
                    # Create rectangle spanning Room 3 and Room 4
                    rect = patches.Rectangle(
                        (2, start_pos),  # Start at Room 3 (index 2)
                        2,  # Span 2 rooms
                        height,
                        linewidth=1,
                        edgecolor="black",
                        facecolor=color,
                        alpha=0.7,
                    )
                    ax.add_patch(rect)

                    # Add class name and teacher name in the middle of the rectangle
                    ax.text(
                        3,  # Center between Room 3 and Room 4
                        start_pos + height / 2,
                        f"{class_data['class_name']}\n{class_data['teacher_name']}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"
                        ),
                    )

                # Handle other combined rooms
                else:
                    # Get the min and max room numbers to span
                    min_room = min(class_data["rooms"]) - 1  # 0-based index
                    max_room = max(class_data["rooms"]) - 1
                    width = max_room - min_room + 1

                    # Create rectangle spanning multiple rooms
                    rect = patches.Rectangle(
                        (min_room, start_pos),
                        width,
                        height,
                        linewidth=1,
                        edgecolor="black",
                        facecolor=color,
                        alpha=0.7,
                    )
                    ax.add_patch(rect)

                    # Add class name and teacher name in the middle of the rectangle
                    ax.text(
                        min_room + width / 2,
                        start_pos + height / 2,
                        f"{class_data['class_name']}\n{class_data['teacher_name']}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"
                        ),
                    )
            else:
                # Single room
                for room_num in class_data["rooms"]:
                    room_idx = room_num - 1  # 0-based index

                    # Create rectangle for this class
                    rect = patches.Rectangle(
                        (room_idx, start_pos),
                        1,
                        height,
                        linewidth=1,
                        edgecolor="black",
                        facecolor=color,
                        alpha=0.7,
                    )
                    ax.add_patch(rect)

                    # Add class name and teacher name
                    ax.text(
                        room_idx + 0.5,
                        start_pos + height / 2,
                        f"{class_data['class_name']}\n{class_data['teacher_name']}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"
                        ),
                    )

    # Create a legend for teacher colors
    legend_handles = [
        patches.Patch(color=teacher_colors[teacher], label=teacher)
        for teacher in sorted_teachers
    ]

    # Add the legend to the figure
    if len(active_days) > 1:
        # For multiple days, place legend at the bottom of the figure
        fig.legend(
            handles=legend_handles,
            loc="lower center",
            ncol=min(5, len(sorted_teachers)),  # Up to 5 columns
            bbox_to_anchor=(0.5, 0),
            fontsize=9,
        )
    else:
        # For a single day, place legend to the right of the plot
        axes[0].legend(
            handles=legend_handles,
            loc="center left",
            bbox_to_anchor=(1.05, 0.5),
            fontsize=9,
        )

    # Adjust layout with space for the legend
    if len(active_days) > 1:
        plt.tight_layout(rect=[0, 0.1, 1, 1])  # Leave space at bottom for legend
    else:
        plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space at right for legend

    # Save figure
    png_path = os.path.join(output_dir, f"{base_filename}.png")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")

    # Optionally save as PDF
    pdf_path = None
    if save_pdf:
        pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
        plt.savefig(pdf_path, format="pdf", bbox_inches="tight")

    # Close the figure to free memory
    plt.close(fig)

    return png_path
