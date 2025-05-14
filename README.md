
# Studio Schedule

An intelligent class scheduling system for dance studios, built in Python using Google OR-Tools.

## Features

- Reads class, teacher, and room availability from an Excel file
- Breaks each day into 15-minute time slots for flexible scheduling
- Assigns classes to rooms, teachers, and times while respecting:
  - Class duration and preferred days/time ranges
  - Teacher and room availability
  - Room group constraints (e.g. accordion walls)
  - Class-specific room and teacher preferences
- Outputs the optimized schedule to Excel or CSV

## Excel Input Format

### classes (sheet)
- class_name
- style
- level
- age_start
- age_end
- duration (in hours)
- preferred_days (comma-separated)
- preferred_time_ranges (e.g. 15:00-18:00, comma-separated)
- preferred_rooms (comma-separated)
- preferred_teachers (comma-separated)

### teachers (sheet)
- teacher_name
- availability (e.g. Monday: 15:00-20:00; Tuesday: 15:00-20:00)

### rooms (sheet)
- room_name
- availability (same format as teachers)
- group (e.g. group 1 for Room 1, Room 2, and Room 1+2)

## Project Architecture

```mermaid
graph TD
    A[Main Program] --> B[Data Loading Module]
    A --> C[Constraint Modeling Module]
    A --> D[Solver Module]
    A --> E[Output Formatting Module]
    B --> F[Excel Data]
    C --> G[CP-SAT Model]
    D --> H[Schedule Solution]
    H --> E
    E --> I[Output Excel/CSV]
```

## Project Structure

```
studio-schedule/
├── data/
│   └── schedule-data.xlsx
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── data_loader.py     # Functions to load and parse Excel data
│   ├── model.py           # CP-SAT model and constraints
│   ├── solver.py          # Solving logic
│   └── output.py          # Output formatting and Excel generation
├── requirements.txt
└── README.md              # Documentation
```


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

### Optional: Install VS Code

We recommend using [Visual Studio Code](https://code.visualstudio.com/) as your editor for this project.

1. Download and install VS Code: https://code.visualstudio.com/
2. Open the project folder (`studio-schedule/`) in VS Code
3. If prompted, install the recommended extensions (such as Python support)
4. Open a terminal in VS Code (`View` > `Terminal`) and run the setup commands:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```


```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

Make sure your `schedule-data.xlsx` file is in the `./data/` directory.

## Requirements

See `requirements.txt` for dependencies. Main ones include:

- ortools
- pandas
- openpyxl

## License

MIT License
