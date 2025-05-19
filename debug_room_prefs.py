"""
Debug utility for room preferences in the Dance Studio Schedule Optimizer.

This script helps debug room preferences and availability by printing
detailed information about room configurations and availability.
"""

from src.data_loader import load_data
from src.room_scheduler import create_room_availability_matrix

# Load data
data = load_data("data/schedule-data.xlsx")

# Print room configurations
print("Room Configurations:")
for room in data["rooms"]:
    room_id = room["room_id"]
    room_name = room["room_name"]
    is_combined = room["is_combined"]
    print(
        f"Room ID: {room_id}, "
        f"Room Name: {room_name}, "
        f"Is Combined: {is_combined}"
    )

# Print class preferences for rooms
print("\nClass Preferences for Rooms:")
for class_id, prefs in data["class_preferences"].items():
    if "room" in prefs:
        print(f"Class ID: {class_id}, Room Preferences: {prefs['room']}")

# Count available slots per room in room_availability
room_avail_counts = {}
for key, value in data["room_availability"].items():
    if value:
        room_id = key[0]
        if room_id not in room_avail_counts:
            room_avail_counts[room_id] = 0
        room_avail_counts[room_id] += 1

print("\nAvailable Slots per Room in room_availability:")
for room_id, count in room_avail_counts.items():
    room_name = next(
        (r["room_name"] for r in data["rooms"] if r["room_id"] == room_id),
        "Unknown",
    )
    output = f"Room ID: {room_id}"
    output += f", Room Name: {room_name}"
    output += f", Available Slots: {count}"
    print(output)

# Create room availability matrix
room_time_slots = create_room_availability_matrix(
    data["rooms"], data["room_availability"]
)

# Print room availability matrix for each room
for room_id in range(1, 7):
    count = 0
    print(f"\nRoom Availability Matrix for Room ID {room_id}:")
    for key, value in room_time_slots.items():
        r_id, day_idx, slot_idx = key
        if r_id == room_id and value and count < 5:
            print(
                f"Room ID: {room_id}, Day: {day_idx}, "
                f"Slot: {slot_idx}, Available: {value}"
            )
            count += 1
    if count == 0:
        print(f"No available slots for Room ID {room_id}")

# Count available slots per room
room_counts = {}
for key, value in room_time_slots.items():
    if value:
        room_id = key[0]
        if room_id not in room_counts:
            room_counts[room_id] = 0
        room_counts[room_id] += 1

print("\nAvailable Slots per Room:")
for room_id, count in room_counts.items():
    room_name = next(
        (r["room_name"] for r in data["rooms"] if r["room_id"] == room_id),
        "Unknown",
    )
    output = f"Room ID: {room_id}"
    output += f", Room Name: {room_name}"
    output += f", Available Slots: {count}"
    print(output)
