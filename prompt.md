## Dance Studio Class Scheduler

I need you to create a Python-based scheduling system for my dance studio that optimizes class assignments based on various constraints. The system should read data from Excel, generate an optimal schedule, and output the results in a well-formatted Excel file.

### Starting Data Structure

I'll provide an Excel file with the following sheets:

1. **classes**:

   - `class_id` (unique identifier)
   - `class_name` (display name)
   - `style` (dance style like Ballet, Jazz)
   - `level` (class level)
   - `age_start` (minimum student age)
   - `age_end` (maximum student age)
   - `duration` (in hours, e.g., 0.75 for 45 minutes)

2. **teacher_availability**:

   - `teacher_id` (unique identifier)
   - `teacher_name`
   - `day` (day of week)
   - `start_time` (in 24-hour format)
   - `end_time` (in 24-hour format)

3. **room_availability**:

   - `room_id` (unique identifier)
   - `room_name`
   - `day` (day of week)
   - `start_time` (in 24-hour format)
   - `end_time` (in 24-hour format)

4. **room_configurations**:

   - `room_id` (unique identifier)
   - `room_name`
   - `is_combined` (TRUE/FALSE - for rooms that can be combined)
   - `component_rooms` (comma-separated list of room names that make up this combined room)

5. **class_preferences**:

   - `class_id` (matches classes sheet)
   - `class_name`
   - `preference_type` (one of: day, time, room, teacher)
   - `preference_value` (the specific value preferred)
   - `weight` (importance of this preference, typically 5-10)

6. **teacher_specializations**:

   - `teacher_id` (matches teacher_availability)
   - `teacher_name`
   - `specialization_type` (style, age_group, level)
   - `specialization_value` (specific value for this specialization)

As part of this project, please also create a template Excel file with these sheets and columns, including a few example rows in each sheet to demonstrate the expected format. This will serve as a guide for entering my studio's actual data.

### System Requirements

Please create a Python application that:

1. **Reads and processes the Excel data**:

   - Parse all sheets into appropriate data structures
   - Convert time ranges into 15-minute time slots for granular scheduling
   - Handle validation and data normalization

2. **Implements a multi-phase scheduling algorithm**:

   - Phase 1: Assign classes to rooms and time slots based on availability and preferences
   - Phase 2: Assign teachers to scheduled classes based on availability and specializations
   - Handle constraints like room conflicts, teacher availability, and class preferences

3. **Handles special scheduling constraints**:

   - Prevent scheduling conflicts between combined rooms and their components
   - Respect teacher specializations when making assignments
   - Consider preference weights when making scheduling decisions
   - Sort classes by scheduling difficulty (prioritize harder-to-schedule classes)

4. **Implements partial scheduling**:

   - Schedule as many classes as possible based on constraints
   - Track unscheduled classes with reasons why they couldn't be placed
   - Provide statistics on scheduling success rate

5. **Generates comprehensive output**:

   - Create an Excel file with multiple sheets for different views
   - Include a main schedule with all classes
   - Create a separate tab for unscheduled classes with reasons
   - Generate room-specific and day-specific schedule tabs

### Code Structure

Please organize the code into the following modules:

1. **main.py**: Entry point with command-line argument handling
2. **data_loader.py**: Functions to load and parse Excel data
3. **room_scheduler.py**: Logic for assigning classes to rooms and time slots
4. **teacher_scheduler.py**: Logic for assigning teachers to scheduled classes
5. **scheduler.py**: Coordination between different scheduling phases
6. **output.py**: Formatting and generating Excel output

### Output Format

The output Excel file should include:

1. **Schedule sheet** with columns:

   - Class ID
   - Class Name
   - Style
   - Level
   - Age Range
   - Day
   - Start Time
   - End Time
   - Duration
   - Room
   - Teacher ID
   - Teacher Name

2. **Unscheduled Classes sheet** with:

   - Class ID
   - Class details (Name, Style, Level, Age Range)
   - Duration
   - Reason why the class couldn't be scheduled

3. **Room-specific sheets** showing classes for each room

4. **Day-specific sheets** showing classes for each day of the week

### Optional Features

If possible, please include these advanced features:

1. **Room combination handling**:

   - Support for rooms that can be combined (e.g., with accordion walls)
   - Proper conflict detection between combined rooms and their components

2. **Preference weighting system**:

   - Consider the weight of preferences when making scheduling decisions
   - Balance between different types of preferences (day, time, room, teacher)

3. **Schedule optimization**:

   - Group similar classes together when possible (same style, sequential levels)
   - Balance class distribution across available days and rooms

4. **Detailed statistics**:

   - Report on scheduling success rate
   - Break down unscheduled classes by reason (room conflicts vs. teacher conflicts)

5. **User-friendly command-line interface**:

   - Support for specifying input file path and output directory
   - Clear progress and error messages

### Implementation Notes

- Use pandas for data manipulation
- Break each day into 15-minute time slots for flexible scheduling
- Sort classes by scheduling difficulty (prioritize harder-to-schedule classes first)
- Use a scoring system to evaluate potential room-time-teacher assignments
- Implement proper error handling and validation

Please create this system with clean, well-documented code that follows Python best practices. The goal is to have a reliable, maintainable scheduling tool that can be used repeatedly as our class offerings change.
