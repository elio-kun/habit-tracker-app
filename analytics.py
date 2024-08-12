from typing import List, Dict, Any
from functools import reduce

class Analytics:
    @staticmethod
    def get_all_habits(habit_objects: List) -> List[str]:
        """
        Returns a list of all currently tracked habits.

        Args:
            habit_objects (List[Habit]): The list of habit objects.

        Returns:
            List[str]: A list of habit names.
        """
        return list(map(lambda habit: habit.name, habit_objects))

    @staticmethod
    def get_habits_by_periodicity(habit_objects: List, periodicity: int) -> List[str]:
        """
        Returns a list of all habits with the same periodicity.

        Args:
            habit_objects (List[Habit]): The list of habit objects.
            periodicity (int): The periodicity to filter by (1=Daily, 2=Weekly, etc.).

        Returns:
            List[str]: A list of habit names with the given periodicity.
        """
        return list(map(lambda habit: habit.name, filter(lambda habit: habit.periodicity == periodicity, habit_objects)))

    @staticmethod
    def get_longest_streak(habit_objects: List) -> str:
        """
        Returns the name of the habit with the longest run streak.

        Args:
            habit_objects (List[Habit]): The list of habit objects.

        Returns:
            str: The name of the habit with the longest streak.
        """
        if not habit_objects:
            return None
        return max(habit_objects, key=lambda habit: habit.streak, default=None)

    @staticmethod
    def get_longest_streak_for_habit(habit_objects: List, habit_name: str) -> int:
        """
        Returns the longest run streak for a given habit.

        Args:
            habit_objects (List[Habit]): The list of habit objects.
            habit_name (str): The name of the habit to find the streak for.

        Returns:
            int: The longest streak for the given habit, or 0 if the habit is not found.
        """
        habit = next((habit for habit in habit_objects if habit.name.lower() == habit_name.lower()), None)
        return habit.longest_streak if habit else 0

    @staticmethod
    def get_most_failed_habit(habit_objects: List) -> str:
        """
        Returns the name of the most often failed habit.

        Args:
            habit_objects (List[Habit]): The list of habit objects.

        Returns:
            str: The name of the most failed habit.
        """
        if not habit_objects:
            return "No habits found."
        habit_most_fails = reduce(lambda x, y: x if x.fails > y.fails else y, habit_objects)
        return habit_most_fails.name if habit_most_fails.fails > 0 else "No fails were found."