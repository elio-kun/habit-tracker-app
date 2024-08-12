import unittest
from datetime import datetime, timedelta
from models import Habit, Decoration
from analytics import Analytics


class TestHabitOperations(unittest.TestCase):
    def setUp(self):
        # Setup predefined data for testing
        self.decoration = Decoration(name="Couch", room="Living Room", state="Old", exp=5)
        self.habit = Habit(name="running", periodicity=1, decoration=self.decoration, streak=4, longest_streak=7)

    def test_habit_creation(self):
        self.assertEqual(self.habit.name, "running")
        self.assertEqual(self.habit.periodicity, 1)
        self.assertEqual(self.habit.streak, 4)
        self.assertEqual(self.habit.longest_streak, 7)

    def test_habit_editing(self):
        self.habit.name = "jogging"
        self.habit.periodicity = 2
        self.assertEqual(self.habit.name, "jogging")
        self.assertEqual(self.habit.periodicity, 2)

    def test_habit_deletion(self):
        habit_list = [self.habit]
        habit_list.remove(self.habit)
        self.assertNotIn(self.habit, habit_list)

    def test_habit_check_in(self):
        self.habit.next_completion_date = datetime.now()
        success = self.habit.check_in()
        self.assertTrue(success)  # Ensure check-in is successful
        self.assertEqual(self.habit.streak, 5)  # Streak should increment
        self.assertEqual(self.habit.longest_streak, 7)  # Longest streak should remain the same

    def test_habit_fail(self):
        self.habit.next_completion_date = datetime.now() - timedelta(days=1)  # Force a fail
        self.habit.calculate_fails()
        self.assertEqual(self.habit.streak, 0)  # Streak should reset
        self.assertEqual(self.habit.longest_streak, 7)  # Longest streak should remain the same


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # Setup predefined habit data
        self.decoration1 = Decoration(name="Couch", room="Living Room", state="Old", exp=5)
        self.decoration2 = Decoration(name="Plant", room="Living Room", state="Good", exp=16)

        self.habit1 = Habit(name="running", periodicity=1, decoration=self.decoration1, streak=4, longest_streak=7)
        self.habit2 = Habit(name="reading", periodicity=1, decoration=self.decoration2, streak=3, longest_streak=5)
        self.habit3 = Habit(name="washing the sheets", periodicity=2, decoration=self.decoration2, streak=4,
                            longest_streak=4)

        self.habit_objects = [self.habit1, self.habit2, self.habit3]

    def test_get_all_habits(self):
        all_habits = Analytics.get_all_habits(self.habit_objects)
        self.assertEqual(all_habits, ["running", "reading", "washing the sheets"])

    def test_get_habits_by_periodicity(self):
        daily_habits = Analytics.get_habits_by_periodicity(self.habit_objects, 1)
        self.assertEqual(daily_habits, ["running", "reading"])

        weekly_habits = Analytics.get_habits_by_periodicity(self.habit_objects, 2)
        self.assertEqual(weekly_habits, ["washing the sheets"])

    def test_get_longest_streak(self):
        longest_streak_habit = Analytics.get_longest_streak(self.habit_objects)
        self.assertEqual(longest_streak_habit.name, "running")
        self.assertEqual(longest_streak_habit.longest_streak, 7)

    def test_get_most_failed_habit(self):
        self.habit1.fails = 10
        self.habit2.fails = 5
        self.habit3.fails = 3

        most_failed_habit = Analytics.get_most_failed_habit(self.habit_objects)
        self.assertEqual(most_failed_habit, "running")

if __name__ == '__main__':
    unittest.main()
