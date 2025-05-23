# Studio Schedule

An intelligent class scheduling system for dance studios, built in Python.

## Features

- Reads class, teacher, and room availability from an Excel file
- Breaks each day into 15-minute time slots for flexible scheduling
- Assigns classes to rooms, teachers, and times while respecting:
  - Class duration and preferred days/time ranges
  - Teacher and room availability
  - Room group constraints (e.g. accordion walls)
  - Class-specific room and teacher preferences
- Handles individual and combined rooms correctly:
  - Prevents scheduling conflicts between combined rooms and their components
  - Properly manages room preferences for both individual and combined spaces
- Implements partial scheduling to maximize class placement:
  - Schedules as many classes as possible based on constraints
  - Tracks unscheduled classes with reasons why they couldn't be placed
- Outputs comprehensive schedule information to Excel with multiple views:
  - Main schedule with all classes
  - Separate tab for unscheduled classes
  - Room-specific schedule tabs
  - Day-specific schedule tabs
- Generates visual weekly schedule representation:
  - Color-coded classes by teacher
  - Classes displayed as blocks spanning horizontally by room and vertically by time
  - Proper handling of combined rooms (spanning multiple columns)
  - Days arranged in vertical sequence from Sunday through Saturday

## Excel Input Format

### `classes` (sheet)

Contains core information about each individual class.

- `class_id` — Unique identifier for the class instance
- `class_name` — Display name (not necessarily unique)
- `style` — Dance style (e.g., Ballet, Jazz)
- `level` — Class level (e.g., IA, IB)
- `age_start` — Minimum student age
- `age_end` — Maximum student age
- `duration` — Class duration in **hours** (e.g., 0.75 for 45 minutes)

### `teacher_availability` (sheet)

Indicates when teachers are available to teach.

- `teacher_id` — Unique ID for the teacher
- `teacher_name`
- `day` - Day of week
- `start_time` - Time in 24-hour format
- `end_time` - Time in 24-hour format

### `room_availability` (sheet)

Defines room availability on a per-day basis.

- `room_id` — Unique ID for the room
- `room_name`
- `day` - Day of week
- `start_time` - Time in 24-hour format
- `end_time` - Time in 24-hour format

### `room_configurations` (sheet)

Describes both individual and combined room options.

- `room_id` — Matches `room_availability` sheet
- `room_name`
- `is_combined` — `TRUE` for combined rooms like Room 1+2
- `component_rooms` — Comma-separated list of subrooms (e.g., `Room 1,Room 2`)

### `class_preferences` (sheet)

Captures preferred scheduling conditions for each class.

- `class_id` - Matches classes sheet
- `class_name`
- `preference_type` — One of: `day`, `time`, `room`, `teacher`
- `preference_value` — The actual preferred value (e.g., `"Monday"` or `"Makeda Hawkins"`)
- `weight` — Priority level (typically 5–10)

### `teacher_specializations` (sheet)

Maps teachers to their qualified teaching areas.

- `teacher_id` - Matches `teacher_availability` sheet
- `teacher_name`
- `specialization_type` — One of: `style`, `age_group`
- `specialization_value` — e.g. `"Jazz"` or `"7-10"`

## Project Architecture

```mermaid
graph TD
    A[Main Program] --> B[Data Loading Module]
    A --> C1[Room Scheduler Module]
    A --> C2[Teacher Scheduler Module]
    A --> D[Scheduler Module]
    A --> E[Output Formatting Module]
    A --> V[Visualization Module]
    B --> F[Excel Data]
    C1 --> D
    C2 --> D
    D --> H[Schedule Solution]
    H --> E
    H --> V
    E --> I[Output Excel/CSV]
    V --> J[Visual Schedule PNG/PDF]
```

## Project Structure

```
studio-schedule/
├── data/
│   ├── schedule-data.xlsx
│   └── schedule-template.xlsx
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── data_loader.py     # Functions to load and parse Excel data
│   ├── room_scheduler.py  # Room scheduling logic
│   ├── teacher_scheduler.py # Teacher assignment logic
│   ├── scheduler.py       # Main scheduling coordination
│   ├── output.py          # Output formatting and Excel generation
│   └── visualization.py   # Schedule visualization generation
├── debug_room_prefs.py    # Utility for debugging room preferences
├── fix_data.py            # Utility for fixing data issues
├── check_overlaps.py      # Utility for checking schedule conflicts
├── requirements.txt
└── README.md              # Documentation
```

## Output Format

The scheduler generates an Excel file with multiple tabs for different views of the schedule:

1. **Schedule**: The main tab containing all scheduled classes with details including:

   - Class Name, Style, Level, Age Range
   - Room and Teacher assignments
   - Day, Start Time, End Time, and Duration

2. **Unscheduled Classes**: A separate tab listing classes that couldn't be scheduled, including:

   - Class details (Name, Style, Level, Age Range, Duration)
   - Reason why the class couldn't be scheduled (e.g., "No compatible room-time slot found")

3. **Room-specific tabs**: Individual tabs for each room showing only the classes scheduled in that room.

4. **Day-specific tabs**: Individual tabs for each day of the week showing the classes scheduled on that day.

This comprehensive output format makes it easy to analyze the schedule from different perspectives and identify any issues or opportunities for improvement.

## Schedule Visualization

The scheduler automatically generates a visual representation of the weekly schedule:

![Sample Schedule Visualization](output/sample_schedule.png)

### Visualization Features

- **Layout**:
  - **Y-axis**: Time of day in 15-minute increments
  - **X-axis**: Rooms (Room 1-4)
  - **Vertical arrangement**: Days of the week from Sunday through Saturday

- **Class Display**:
  - Each class is represented as a colored block
  - Block position is based on start time and room
  - Block height is proportional to class duration
  - Each block is labeled with class name and teacher name
  - Classes are color-coded by teacher (with legend)

- **Room Handling**:
  - Combined rooms (e.g., Room 1+2) are displayed as blocks spanning multiple columns
  - All four rooms (Room 1-4) are always displayed

- **Output**:
  - Visualization is saved as a PNG file in the output directory
  - File naming matches the Excel output (e.g., `schedule_20250520_085837.png`)

## Using the Schedule Template

A pre-formatted Excel file is available at `./data/schedule-template.xlsx` to help you get started.

### Instructions

1. Open `schedule-template.xlsx` in Excel or Google Sheets.
2. Fill out each sheet:
   - **classes**: Add your studio’s classes, styles, age ranges, durations, and preferences.
   - **teachers**: List each teacher and their availability by day and time range.
   - **rooms**: Enter your studio rooms, their availability, and group identifiers (used for combined spaces like Room 1+2).
3. Sample rows are included in each sheet for reference. **Please delete these before running the program**, but **do not change the column headers or sheet names**.
4. Save the file (keeping the same structure and sheet names).
5. Place the file in the `./data/` folder before running the program.

### Formatting Rules

- **Days and time values** should be entered in the format:
  - `Monday:15:15-18:00,Tuesday:16:00-20:00`
- Use **commas with no spaces** between entries.
- Ensure all time values use **24-hour format** (`HH:MM`).

**Important:** Do not rename the sheets or change the column names — the program relies on exact matches.

## Installation

### Optional: Install Python and Git

These tools are commonly used with this project. Install them if they’re not already available on your system.

#### Install Python

1. Visit the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest stable version of **Python 3.9 or higher**
3. During installation:
   - ✅ Check the box that says **"Add Python to PATH"**
4. Verify installation in a terminal or command prompt:
   ```bash
   python --version
   ```
   **Note:** If the command above doesn't work or shows an older version (e.g., Python 2.7), try using python3 instead:

```bash
python3 --version
```

#### Install Git

1. Visit: [https://git-scm.com/downloads](https://git-scm.com/downloads)
2. Download and install the latest version for your operating system
3. Confirm installation:
   ```bash
   git --version
   ```

Git is helpful for downloading this repo and managing changes, especially if you're syncing updates or collaborating.

### Optional: Install VS Code

I recommend using [Visual Studio Code](https://code.visualstudio.com/) as your editor for this project.

1. Download and install VS Code: https://code.visualstudio.com/
2. Open the project folder (`studio-schedule/`) in VS Code
3. If prompted, install the recommended extensions (such as Python support)

### Setup

Open a terminal in VS Code (`View` > `Terminal`) and run the setup commands:

1. Clone this GitHub repo:

```bash
git clone https://github.com/shonlittle/studio-schedule.git
cd studio-schedule
```

2. Create a Python virtual environment:

```bash
python -m venv .venv # or in some cases python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

**Tip:** On some systems (especially macOS or Linux), use `python3` instead of `python` if you get a `python: command not found` error.

3. Install third-party requirements:

```bash
pip install -r requirements.txt
```

## Usage

Terminal command line to run the scheduler:

```bash
python src/main.py [--data DATA_FILE] [--output OUTPUT_DIR]
```

### Command-line Arguments

- `--data` or `-d`: Path to the Excel file containing schedule data (default: `data/schedule-data.xlsx`)
- `--output` or `-o`: Directory to save output files (default: `output`)
- `--no-visuals`: Skip generation of schedule visualization

### Example Usage

```bash
# Use default data file and output directory
python src/main.py

# Specify a different data file
python src/main.py --data data/my-schedule-data.xlsx

# Specify both data file and output directory
python src/main.py --data data/my-schedule-data.xlsx --output my-output

# Run without generating visualization
python src/main.py --no-visuals
```

The program will generate an Excel file with the optimized schedule in the specified output directory. The file will be named with a timestamp (e.g., `schedule_20250517_174510.xlsx`).

### Statistics

After scheduling is complete, the program will display statistics including:

- Total number of classes
- Number of scheduled classes
- Number of unscheduled classes
- Scheduling rate (percentage of classes scheduled)
- Number of classes unscheduled due to room conflicts
- Number of classes unscheduled due to teacher conflicts

## Requirements

See `requirements.txt` for dependencies. Main ones include:

- pandas (>= 1.4.0): For data manipulation and analysis
- openpyxl (>= 3.0.0): For Excel file reading and writing
- matplotlib (>= 3.5.0): For schedule visualization generation

## License

GNU General Public License
