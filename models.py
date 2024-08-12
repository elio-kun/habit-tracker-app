import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import random
from utils import get_day_with_suffix, wrapped_message, type_ok, empty_list
from file_manager import FileManager
from analytics import Analytics

class Decoration:
    """
    Represents a decoration with states and experience points (EXP).

    Attributes:
        name (str): The name of the decoration.
        room (str): The room where the decoration is located.
        state (str): The current state of the decoration.
        exp (int): The current experience points of the decoration.
    """

    # EXP thresholds and corresponding states
    exp_states = {0: "Old", 16: "Normal", 32: "Good", 64: "Great"}

    # For filtering decorations
    decor_criteria_map = {
        'name': lambda decor: decor.name,
        'room': lambda decor: decor.room,
        'state': lambda decor: decor.state,
        'exp': lambda decor: decor.exp
    }

    def __init__(self, name: str, room: str, state: str, exp: int):
        self.name = name
        self.room = room
        self.state = state
        self.exp = exp

    def __repr__(self) -> str:
        return f"Decoration: {self.name}; Room: {self.room}; State: {self.state}; EXP: {self.exp}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Decoration):
            return (self.name == other.name and
                    self.room == other.room and
                    self.state == other.state)
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.room, self.state))

    def update_state(self):
        """
        Updates the state of the decoration based on its EXP.
        Logs the change and notifies the user if the state is upgraded or downgraded.
        """
        previous_state = self.state

        # Determine the new state based on current EXP
        for exp_threshold, state in sorted(Decoration.exp_states.items(), reverse=True):
            if self.exp >= exp_threshold:
                self.state = state
                break

        # If the state has changed, log the change and notify the user
        if self.state != previous_state:
            FileManager.logger.info(f"The decoration {self.name} was updated to {self.state}.")
            previous_state_index = list(Decoration.exp_states.values()).index(previous_state)
            new_state_index = list(Decoration.exp_states.values()).index(self.state)

            if new_state_index > previous_state_index:
                wrapped_message(f"Congratulations!"
                                f"\nThe decoration {self.name} was upgraded to {self.state} state!"
                                f"\nLooks better now!", 70)
            else:
                wrapped_message(f"The decoration {self.name} was downgraded to {self.state} state. "
                                f"\nDon't give up! Keep working to improve it!", 70)
            return


class Habit:
    """
    Represents a habit with a periodicity and associated decoration.

    Attributes:
        name (str): The name of the habit.
        periodicity (int): The periodicity of the habit (1=Daily, 2=Weekly, 3=Monthly, 4=Yearly).
        decoration (Decoration): The decoration associated with the habit.
        next_completion_date (datetime): The next date when the habit should be completed.
        fails (int): The number of times the habit has been missed.
        streak (int): The current streak of successful completions.
        longest_streak (int): The longest streak of successful completions.
    """

    # EXP values based on periodicity
    exp_values = {1: 1, 2: 8, 3: 16, 4: 32}

    # Map periodicity numbers to words
    periodicity_map = {1: "Daily", 2: "Weekly", 3: "Monthly", 4: "Yearly"}

    # For displaying the habit tables
    habit_criteria_map = {
        'name': lambda habit: habit.name,
        'periodicity': lambda habit: habit.periodicity,
        'room': lambda habit: habit.decoration.room,
        'next_completion_date': lambda habit: habit.next_completion_date,
        'fails': lambda habit: habit.fails,
        'streak': lambda habit: habit.streak,
        'l_streak': lambda habit: habit.longest_streak
    }

    def __init__(self, name: str, periodicity: int, decoration: Decoration,
                 next_completion_date: Optional[datetime] = None, fails: int = 0, streak: int = 0, longest_streak: int = 0):
        self.name = name
        self.periodicity = periodicity
        self.decoration = decoration
        self.next_completion_date = next_completion_date or self.calculate_completion_date()
        self.fails = fails
        self.streak = streak
        self.longest_streak = longest_streak

    def __repr__(self) -> str:
        return (f"Habit: {self.name}; Periodicity: {self.periodicity}; "
                f"Decoration: {self.decoration.name}; Room: {self.decoration.room}; "
                f"Check-in Day: {self.formatted_date}; Fails: {self.fails}; Streak: {self.streak}")

    @property
    def formatted_date(self) -> str:
        """Returns the formatted next completion date."""
        if self.next_completion_date:
            day_with_suffix = get_day_with_suffix(self.next_completion_date.day)
            return self.next_completion_date.strftime(f"%B {day_with_suffix}, %Y" if self.periodicity == 4 else f"%B {day_with_suffix}")
        return "N/A"

    def increment_completion_date(self, date: datetime) -> datetime:
        """Increments the provided date by the habit's periodicity."""
        if self.periodicity == 1:  # Daily
            return date + timedelta(days=1)
        elif self.periodicity == 2:  # Weekly
            return date + timedelta(weeks=1)
        elif self.periodicity == 3:  # Monthly
            return date.replace(month=(date.month % 12) + 1, year=date.year + (date.month // 12), day=min(date.day, 28))
        elif self.periodicity == 4:  # Yearly
            return date.replace(year=date.year + 1)
        raise ValueError("Invalid periodicity value.")

    def calculate_completion_date(self) -> datetime:
        """Calculates the next completion date based on the habit's periodicity."""
        return self.increment_completion_date(datetime.now())

    def calculate_fails(self) -> bool:
        """
        Calculates the number of fails based on the original next completion date and the current date.

        Returns:
            bool: True if fails were detected, False otherwise.
        """
        now = datetime.now()
        fails_detected = False

        while now > self.next_completion_date.replace(hour=23, minute=59, second=59):
            self.next_completion_date = self.increment_completion_date(self.next_completion_date)
            self.fails += 1
            fails_detected = True

        if fails_detected:
            # Update longest streak if current streak is greater
            if self.streak > self.longest_streak:
                self.longest_streak = self.streak
            self.streak = 0  # Reset the current streak after a fail

        return fails_detected

    def check_in(self) -> bool:
        """
        Checks in the habit and updates streak or fails based on the completion date.

        Returns:
            bool: True if check-in was successful, False otherwise.
        """
        now = datetime.now()
        completion_date_start = self.next_completion_date.replace(hour=0, minute=0, second=0)
        completion_date_end = self.next_completion_date.replace(hour=23, minute=59, second=59)

        if now < completion_date_start:
            day_with_suffix = get_day_with_suffix(self.next_completion_date.day)
            formatted_date = self.next_completion_date.strftime(f"%B {day_with_suffix}")
            FileManager.logger.warning(f"Attempted early check-in for {self.name}.")
            wrapped_message(f"It's too early to check-in for {self.name}!"
                            f"\nPlease try again during this day: {formatted_date}.", 50)
            type_ok()
            return False

        if completion_date_start <= now <= completion_date_end:
            self.streak += 1
            self.decoration.exp += self.exp_values.get(self.periodicity, 0)
            FileManager.logger.info(f"Successfully checked in for {self.name}. "
                                    f"Streak: {self.streak}, EXP: {self.decoration.exp}.")

            self.decoration.update_state()

            self.next_completion_date = self.increment_completion_date(self.next_completion_date)
            FileManager.logger.debug(f"Next completion date for {self.name} set to {self.next_completion_date}.")
            if self.streak > self.longest_streak:
                self.longest_streak = self.streak
                wrapped_message(f"Successfully checked in for {self.name}!"
                                f"\nYou beat your record! Your longest streak is now {self.longest_streak}."
                                f"\nYour next completion date is {self.formatted_date}.", 50)
            else:
                wrapped_message(f"Successfully checked in for {self.name}!"
                                f"\nStreak: {self.streak}, EXP: {self.decoration.exp}."
                                f"\nYour longest streak for this habit is {self.longest_streak}."
                                f"\nYour next completion date is {self.formatted_date}.", 50)

            type_ok()
            return True

        return False

    def reset_decoration(self):
        """Resets the decoration associated with this habit."""
        self.decoration.exp = 0
        self.decoration.state = "Old"
        FileManager.logger.info(f"Decoration '{self.decoration.name}' linked to habit '{self.name}' was reset.")
        print(f"The decoration '{self.decoration.name}' linked to habit '{self.name}' was reset and is now free!")


class Butler:
    """
    Represents a Butler with a name, age, appearance, and personality.

    Attributes:
        name (str): The Butler's name.
        age (int): The Butler's age.
        appearance (str): The Butler's appearance description.
        personality_flag (str): The flag representing the Butler's personality type.
        description (str): The description of the Butler's personality.
    """

    def __init__(self, name: str, age: int, appearance: str, personality_flag: str, description: str):
        self.name = name
        self.age = age
        self.appearance = appearance
        self.personality_flag = personality_flag
        self.description = description

    def __repr__(self) -> str:
        return (f"Butler: {self.name}; Age: {self.age}; Appearance: {self.appearance}; "
                f"Personality: {self.description}")

    @staticmethod
    def generate_butler(butler_options: Dict[str, Any]) -> 'Butler':
        """
        Generates a new Butler using options from the butler_options.json file.

        Args:
            butler_options (Dict[str, Any]): The options for generating a Butler.

        Returns:
            Butler: The generated Butler object.
        """
        name = random.choice(butler_options['names'])
        age = random.randint(21, 112)
        appearance = random.choice(butler_options['appearances'])
        personality_flag = random.choice(list(butler_options['personalities'].keys()))
        description = butler_options['personalities'][personality_flag]['description']

        new_butler = Butler(name, age, appearance, personality_flag, description)

        # Save the new butler to current_butler.json as a dictionary
        FileManager.save_data('current_butler.json', new_butler.__dict__)
        new_butler.display_info()

        return new_butler

    def talk_to(self, butler_options: Dict[str, Any]):
        """
        Generates a random replica based on the Butler's personality.

        Args:
            butler_options (Dict[str, Any]): The options for the Butler's replicas.
        """
        replicas = butler_options['personalities'][self.personality_flag]['replicas']
        wrapped_message(f"{self.name} says: {random.choice(replicas)}", 50)
        type_ok()

    def display_info(self):
        """Displays the Butler's information."""
        wrapped_message("Here's your Butler's information:", 50)
        print(f"Name: {self.name}\nAge: {self.age}"
              f"\nAppearance: {self.appearance}\nPersonality: {self.description}")
        type_ok()

    def provide_analytics(self, habit_objects: List[Habit]):
        """
        Provides detailed analytics using the Analytics module.

        Args:
            habit_objects (List[Habit]): The list of habits to analyze.
        """
        wrapped_message("HABIT ANALYSIS", 50)

        if not habit_objects:
            print("No habits found to analyze.")
            type_ok()
            return

        all_habits = Analytics.get_all_habits(habit_objects)
        print(f"Your current habits are: {', '.join(all_habits)}")

        periodicities = ['Daily', 'Weekly', 'Monthly', 'Yearly']
        for i, period in enumerate(periodicities, start=1):
            habits_by_period = Analytics.get_habits_by_periodicity(habit_objects, i)
            print(f"{period}: {', '.join(habits_by_period)}")

        longest_streak_habit = Analytics.get_longest_streak(habit_objects)
        if longest_streak_habit:
            print(
                f"Your current biggest streak is {longest_streak_habit.streak} of the habit {longest_streak_habit.name}!")

        longest_streak_all_time = Analytics.get_longest_streak(habit_objects)  # Use the appropriate method here
        if longest_streak_all_time:
            print(
                f"Your biggest streak of all time is {longest_streak_all_time.streak} of the habit {longest_streak_all_time.name}!")

        most_failed_habit = Analytics.get_most_failed_habit(habit_objects)
        if most_failed_habit:
            print(
                f"Your most often failed habit is {most_failed_habit}. Don't get upset; perhaps you should rethink your approach?")

        type_ok()
