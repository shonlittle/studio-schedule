"""
Visualization module for the Dance Studio Schedule Optimizer.

This module contains functions for creating visual representations of the
schedule, including a weekly schedule visualization with classes mapped by
room and time.
"""

import os
from datetime import datetime, timedelta

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
    # Create visuals directory if it doesn't exist
    visuals_dir = os.path.join(output_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    # Read the Excel file
    schedule_df = pd.read_excel(schedule_file, sheet_name="Schedule")

    # Process the data for visualization
    days_data = process_schedule_data(schedule_df)

    # Create the visualization
    fig_path = create_weekly_visualization(days_data, visuals_dir, save_pdf)

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
            # Split the combined room into individual rooms
            room_parts = room.split("+")
            for part in room_parts:
                # Clean up room name and extract room number
                clean_part = part.strip()
                if "Room" in clean_part:
                    room_num = int(clean_part.replace("Room", "").strip())
                    rooms_to_use.append(room_num)
        else:
            # Single room, extract room number
            if "Room" in room:
                room_num = int(room.replace("Room", "").strip())
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
        }

        # Add to the appropriate day
        days_data[day].append(class_data)

    return days_data


def create_weekly_visualization(days_data, output_dir, save_pdf=False):
    """
    Create a weekly visualization of the schedule.

    Args:
        days_data (dict): Dictionary with processed data for each day.
        output_dir (str): Directory to save the visualization.
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

    # Calculate number of 15-minute slots
    time_slots = int((latest_end - earliest_start).total_seconds() / (15 * 60))

    # Create figure with subplots for each day
    fig_height = 2 + (time_slots * 0.25)  # Scale height based on time range
    fig_width = 12  # Fixed width

    fig, axes = plt.subplots(
        len(active_days),
        1,
        figsize=(fig_width, fig_height),
        gridspec_kw={"height_ratios": [time_slots] * len(active_days)},
    )

    # Handle case with only one day
    if len(active_days) == 1:
        axes = [axes]

    # Set up color map for classes
    cmap = plt.cm.get_cmap("tab20", 20)

    # Process each day
    for i, day in enumerate(active_days):
        ax = axes[i]

        # Set up the grid
        ax.set_xlim(0, 4)  # 4 rooms
        ax.set_ylim(0, time_slots)

        # Add room labels on x-axis
        ax.set_xticks([0.5, 1.5, 2.5, 3.5])
        ax.set_xticklabels(["Room 1", "Room 2", "Room 3", "Room 4"])

        # Add time labels on y-axis
        time_labels = []
        current_time = earliest_start
        for _ in range(time_slots + 1):
            time_labels.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)

        # Place time labels every hour (4 slots)
        y_ticks = np.arange(0, time_slots + 1, 4)
        y_labels = [time_labels[i] for i in y_ticks]
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
            # Calculate position and size
            start_slot = (class_data["start_time"] - earliest_start).total_seconds() / (
                15 * 60
            )
            height = class_data["duration"] * 4  # 4 slots per hour

            # Get color for this class (cycle through colormap)
            color = cmap(j % 20)

            # Handle combined rooms
            if class_data["is_combined"]:
                # Get the min and max room numbers to span
                min_room = min(class_data["rooms"]) - 1  # 0-based index
                max_room = max(class_data["rooms"]) - 1
                width = max_room - min_room + 1

                # Create rectangle spanning multiple rooms
                rect = patches.Rectangle(
                    (min_room, start_slot),
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
                    start_slot + height / 2,
                    f"{class_data['class_name']}\n{class_data['teacher_name']}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    bbox=dict(facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"),
                )
            else:
                # Single room
                for room_num in class_data["rooms"]:
                    room_idx = room_num - 1  # 0-based index

                    # Create rectangle for this class
                    rect = patches.Rectangle(
                        (room_idx, start_slot),
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
                        start_slot + height / 2,
                        f"{class_data['class_name']}\n{class_data['teacher_name']}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"
                        ),
                    )

    # Adjust layout
    plt.tight_layout()

    # Save figure
    png_path = os.path.join(output_dir, "full_week_schedule.png")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")

    # Optionally save as PDF
    pdf_path = None
    if save_pdf:
        pdf_path = os.path.join(output_dir, "full_week_schedule.pdf")
        plt.savefig(pdf_path, format="pdf", bbox_inches="tight")

    # Close the figure to free memory
    plt.close(fig)

    return png_path
