"""
Main module for the Dance Studio Schedule Optimizer.

This module contains the main entry point for the program.
"""

import argparse
import os
import sys
import time

from src.data_loader import load_data
from src.model import create_model
from src.output import create_schedule_output
from src.solver import get_solution_stats, solve_schedule


def main():
    """Main entry point for the program."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dance Studio Schedule Optimizer")
    parser.add_argument(
        "--data",
        type=str,
        default="data/schedule-data.xlsx",
        help="Path to the Excel file containing schedule data",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to save the output file",
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=60,
        help="Time limit for solving in seconds",
    )
    args = parser.parse_args()

    # Check if data file exists
    if not os.path.exists(args.data):
        print(f"Error: Data file '{args.data}' not found.")
        sys.exit(1)

    # Check if output directory exists
    if not os.path.exists(args.output_dir):
        print(f"Error: Output directory '{args.output_dir}' not found.")
        sys.exit(1)

    # Load data
    print(f"Loading data from '{args.data}'...")
    try:
        classes, teachers, rooms = load_data(args.data)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    print(
        f"Loaded {len(classes)} classes, {len(teachers)} teachers, and {len(rooms)} rooms."
    )

    # Create model
    print("Creating constraint model...")
    start_time = time.time()
    model, variables = create_model(classes, teachers, rooms, relax_constraints=False)
    model_time = time.time() - start_time
    print(f"Model created in {model_time:.2f} seconds.")

    # Solve model
    print(f"Solving schedule (time limit: {args.time_limit} seconds)...")
    start_time = time.time()
    status, schedule = solve_schedule(model, variables, classes, args.time_limit)
    solve_time = time.time() - start_time
    print(f"Solving completed in {solve_time:.2f} seconds with status: {status}")

    # Check if solution is feasible
    if status in ["OPTIMAL", "FEASIBLE"]:
        # Get solution statistics
        stats = get_solution_stats(schedule, classes, rooms, teachers)
        print(
            f"Scheduled {stats['scheduled_classes']} out of {stats['total_classes']} classes "
            f"({stats['scheduling_rate'] * 100:.1f}%)."
        )

        # Create output file
        print("Creating output file...")
        output_file = create_schedule_output(schedule, rooms, teachers, args.output_dir)
        print(f"Schedule saved to '{output_file}'.")

        # Print room utilization
        print("\nRoom Utilization:")
        for room_name, count in stats["room_utilization"].items():
            print(f"  {room_name}: {count} classes")

        # Print teacher utilization
        print("\nTeacher Utilization:")
        for teacher_name, count in stats["teacher_utilization"].items():
            if not teacher_name.endswith("_days"):
                days = stats["teacher_utilization"].get(f"{teacher_name}_days", 0)
                print(f"  {teacher_name}: {count} classes across {days} days")

        return 0
    else:
        print("No feasible solution found. Please check the constraints and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
