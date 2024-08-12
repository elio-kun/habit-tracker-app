from typing import List, Dict, Any
import random
from datetime import datetime
from models import Habit, Decoration, Butler

class Conversion:
    """Handles conversion between JSON data and Python objects."""

    rooms = ["Living Room", "Bedroom", "Home Office"]
    decor_names = ["Sofa", "Armchair", "Coffee Table", "Rug", "Pillow"]

    @staticmethod
    def serialize_habits(habit_objects: List[Habit]) -> List[Dict[str, Any]]:
        """
        Converts a list of Habit objects into a serializable format for JSON.

        Args:
            habit_objects (List[Habit]): The list of Habit objects to serialize.

        Returns:
            List[Dict[str, Any]]: The serialized habit data.
        """
        serialized_habits = []
        for habit in habit_objects:
            habit_dict = habit.__dict__.copy()
            if habit_dict['next_completion_date']:
                habit_dict['next_completion_date'] = habit_dict['next_completion_date'].isoformat()
            if isinstance(habit_dict['decoration'], Decoration):
                habit_dict['decoration'] = habit_dict['decoration'].__dict__
            serialized_habits.append(habit_dict)
        return serialized_habits

    @staticmethod
    def convert_habit(habit_data: Dict[str, Any], decor_objects: List['Decoration']) -> 'Habit':
        """
        Converts a dictionary from JSON into a Habit object.

        Args:
            habit_data (Dict[str, Any]): The habit data from JSON.

        Returns:
            Habit: The converted Habit object.
        """
        corrupted_fields = []

        # Handle next_completion_date
        try:
            if 'next_completion_date' in habit_data and habit_data['next_completion_date']:
                habit_data['next_completion_date'] = datetime.fromisoformat(habit_data['next_completion_date'])
            else:
                raise KeyError('next_completion_date')
        except (KeyError, ValueError):
            habit_data['next_completion_date'] = None
            corrupted_fields.append('next_completion_date')

        # Handle missing name
        if 'name' not in habit_data or not habit_data['name']:
            habit_data['name'] = random.choice(string.ascii_letters)
            corrupted_fields.append('name')

        # Handle missing periodicity
        if 'periodicity' not in habit_data or not habit_data['periodicity']:
            habit_data['periodicity'] = 1
            corrupted_fields.append('periodicity')

        # Handle missing decoration
        if 'decoration' in habit_data and isinstance(habit_data['decoration'], dict):
            matched_decor = next((decor for decor in decor_objects if
                                  decor.name == habit_data['decoration']['name'] and
                                  decor.room == habit_data['decoration']['room'] and
                                  decor.state == habit_data['decoration']['state']), None)

            habit_data['decoration'] = matched_decor if matched_decor else Conversion.convert_decor(habit_data['decoration'])
        else:
            habit_data['decoration'] = random.choice(decor_objects) if decor_objects else None
            corrupted_fields.append('decoration')

        current_habit = Habit(**habit_data)

        if corrupted_fields:
            corrupted_data.append(f"Habit '{current_habit.name}': changed fields - {', '.join(corrupted_fields)}")

        return current_habit

    @staticmethod
    def convert_decor(decor_data: Dict[str, Any]) -> Decoration:
        """
        Converts a decoration dictionary from JSON into a Decoration object with default values for missing attributes.

        Args:
            decor_data (Dict[str, Any]): The decoration data from JSON.

        Returns:
            Decoration: The converted Decoration object.
        """
        corrupted_fields = []

        # Handle missing name
        if 'name' not in decor_data or not decor_data['name']:
            decor_data['name'] = random.choice(Conversion.decor_names)
            corrupted_fields.append('name')

        # Handle missing room
        if 'room' not in decor_data or not decor_data['room']:
            decor_data['room'] = random.choice(Conversion.rooms)
            corrupted_fields.append('room')

        # Handle missing state
        if 'state' not in decor_data or not decor_data['state']:
            decor_data['state'] = "Old"
            corrupted_fields.append('state')

        # Handle missing exp
        if 'exp' not in decor_data:
            decor_data['exp'] = 0
            corrupted_fields.append('exp')

        decoration = Decoration(**decor_data)

        if corrupted_fields:
            corrupted_data.append(f"Decoration '{decoration.name}': changed fields - {', '.join(corrupted_fields)}")

        return decoration
