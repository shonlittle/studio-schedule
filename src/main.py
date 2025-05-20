"""
Main module for the Dance Studio Schedule Optimizer.

This module serves as the entry point for the scheduling system.
"""

import argparse
import os
import sys
from datetime import datetime

from scheduler import schedule_classes


def main():
    """
    Main function to run the scheduling system.
    """
    # Parse command line arguments
    desc = "Dance Studio Schedule Optimizer"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--data",
        "-d",
        type=str,
        default="data/schedule-data.xlsx",
        help="Path to the Excel file with schedule data",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output",
        help="Directory to save output files",
    )
    parser.add_argument(
        "--no-visuals",
        action="store_true",
        help="Skip generation of schedule visualization",
    )
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.data):
        print(f"Error: Input file '{args.data}' not found.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Print start message
    print(f"Starting Dance Studio Schedule Optimizer at {datetime.now()}")
    print(f"Input file: {args.data}")
    print(f"Output directory: {args.output}")
    print("=" * 50)

    try:
        # Run the scheduler
        create_visuals = not args.no_visuals
        output_file, stats = schedule_classes(
            args.data, args.output, create_visuals
        )

        # Print statistics
        print("\nScheduling completed successfully!")
        print(f"Output file: {output_file}")
        print("\nStatistics:")
        print(f"  Total classes: {stats['total_classes']}")
        print(f"  Scheduled classes: {stats['scheduled_classes']}")
        print(f"  Unscheduled classes: {stats['unscheduled_classes']}")
        print(f"  Scheduling rate: {stats['scheduling_rate']:.2%}")
        room_conflicts = stats["unscheduled_by_room"]
        teacher_conflicts = stats["unscheduled_by_teacher"]
        print(f"  Unscheduled (room conflicts): {room_conflicts}")
        print(f"  Unscheduled (teacher conflicts): {teacher_conflicts}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
