import builtins
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from models import Habit, Decoration, Butler
from file_manager import FileManager
from conversion import Conversion
from utils import wrapped_message, type_ok, empty_list, choice_check

# Save the original input function
original_input = builtins.input

def custom_input(prompt: str) -> str:
    """Custom input function that returns to the main menu if the user types 'x'."""
    user_input = original_input(prompt).strip().lower()
    if user_input == 'x':
        print("Returning to main menu...")
        main_menu()
    return user_input

# Override the built-in input function
builtins.input = custom_input


def saving():
    """Save the current state of habits and decorations to their respective JSON files."""
    FileManager.save_data('habits.json', Conversion.serialize_habits(habit_objects))
    FileManager.save_data('decorations.json', [decor.__dict__ for decor in decor_objects])


def giving_list(items: List[Any]) -> bool:
    """Print a numbered list of items with specific formatting for Habits and Decorations."""
    if empty_list(items):
        return False

    # Determine the maximum width for each column
    max_name_len = max(len(getattr(item, 'name', '')) for item in items) + 2
    max_date_len = max(len(getattr(item, 'formatted_date', 'N/A')) for item in items) + 2
    number_width = len(str(len(items)))  # This gives the width of the largest number

    # Print the list with alignment
    for i, thing in enumerate(items, start=1):
        if isinstance(thing, Habit):
            periodicity_str = Habit.periodicity_map.get(thing.periodicity, "Unknown")
            print(f"{str(i).rjust(number_width)}. {thing.name.ljust(max_name_len)} | "
                  f"{periodicity_str.ljust(7)} | "
                  f"Decoration: {thing.decoration.name.ljust(max_name_len)} | "
                  f"Next Completion Date: {thing.formatted_date.ljust(max_date_len)} | "
                  f"Current Streak: {thing.streak} | "
                  f"Longest Streak: {thing.longest_streak} | "
                  f"{thing.fails} Fails")
        elif isinstance(thing, Decoration):
            print(f"{str(i).rjust(number_width)}. {thing.name.ljust(max_name_len)} | "
                  f"{thing.room.ljust(13)} | "
                  f"{thing.state.ljust(7)} | "
                  f"{str(thing.exp)} EXP")
        else:
            print(f"{i}. {thing}")  # Default printing for any other object type

    return True


def filter_items(items: List[Any], criterion: str, criteria_map: Dict[str, Callable[[Any], Any]]) -> List[Any]:
    """Filters and sorts the list of items based on the given criterion."""
    if criterion not in criteria_map:
        raise ValueError("Invalid criterion.")

    reverse = criterion in ['fails', 'streak', 'l_streak', 'exp']  # Reverse order for certain criteria

    return sorted(items, key=criteria_map[criterion], reverse=reverse)


def filter_items_menu(items: List[Any], criteria_map: Dict[str, Callable[[Any], Any]]):
    """Filter and display items based on a chosen criterion."""
    if empty_list(items):
        return

    while True:
        print(f"\nHere's your available criteria: {', '.join(criteria_map.keys())}")

        criterion = input("Please type the chosen criterion: ").strip().lower()

        try:
            filtered_items = filter_items(items, criterion, criteria_map)
            break  # Exit the loop if the criterion is valid
        except ValueError as e:
            print(f"\n{e}")

    wrapped_message(f"Here's a list of your items, filtered by {criterion}:", 70)
    giving_list(filtered_items)


def view_items(items: List[Any], criteria_map: Dict[str, Callable[[Any], Any]], is_habit: bool = False, action: Optional[str] = None):
    """View all items (habits or decorations) and allow editing, deletion, filtering, or other actions."""
    if not giving_list(items):
        return

    if action == "check_in" and is_habit:
        print("\nFirst, let's choose what to check-in!")
        choice = choice_check(len(items))
        items[choice - 1].check_in()
        saving()
        return

    while True:
        # Display appropriate options based on item type
        if is_habit:
            print("\nWhat would you like to do now?"
                  "\n1. Edit/Delete a certain habit"
                  "\n2. Filter habits by a criterion..."
                  "\n3. Go back")
            sub_choice = choice_check(3)
        else:
            print("\nWhat would you like to do now?"
                  "\n1. Filter decorations by a criterion..."
                  "\n2. Go back")
            sub_choice = choice_check(2)

        if is_habit and sub_choice == 1:
            if len(items) == 1:
                # If there's only one habit, directly proceed to edit/delete it
                edit_habit(items[0])
            else:
                print("\nWhat habit are you interested in?")
                choice = choice_check(len(items))
                edit_habit(items[choice - 1])
        elif (is_habit and sub_choice == 2) or (not is_habit and sub_choice == 1):
            filter_items_menu(items, criteria_map)
        else:
            break

        saving()


def create_new_habit():
    """Creates a new habit and adds it to the JSON file."""
    wrapped_message("CREATING A HABIT", 50)
    print("Let's go! First, please choose a decoration from the list.")
    giving_list(decor_objects)
    choice = choice_check(len(decor_objects))
    decoration = decor_objects[choice - 1]

    # Perform the decor_check
    if not decor_check(decoration, habit_objects):
        print("\nHabit creation canceled.")
        return  # Stop here without calling main_menu or saving

    name = get_habit_name()
    periodicity = get_periodicity()

    next_completion_date = None
    new_habit = Habit(name, periodicity, decoration, next_completion_date, fails=0, streak=0, longest_streak=0)
    new_habit.decoration.exp = 0
    habit_objects.append(new_habit)
    saving()

    print(
        f"\nYour new habit, {new_habit.name}, is created! "
        f"\nDon't forget to check in on this day: {new_habit.formatted_date}!")
    type_ok()


def get_habit_name() -> str:
    """Prompt the user for a habit name and ensure it is less than 32 characters."""
    name = input("\nWhat's the name of the habit? ")
    while len(name) > 32:
        FileManager.logger.warning("Invalid habit name length. Expected less than 32 characters.")
        name = input("\nInvalid input. Please make the name less than 32 characters long.")
    return name


def get_periodicity() -> int:
    """Prompt the user to select the periodicity of the habit."""
    print("\nWhat's the periodicity?"
          "\n1. Daily"
          "\n2. Weekly"
          "\n3. Monthly"
          "\n4. Yearly")
    return choice_check(4)


def decor_check(decoration: Decoration, habit_objects: List[Habit], current_habit: Optional[Habit] = None) -> bool:
    """Check if the decoration is already linked to another habit."""
    for habit in habit_objects:
        if habit.decoration == decoration and habit != current_habit:
            print(f"\nWARNING: Decoration {decoration.name} is already linked to the habit {habit.name}!"
                  "\nChoosing it will delete the existing habit and EXP, creating a new one.")
            while True:
                proceed = input("\nDo you want to proceed? (yes/no): ").strip().lower()
                if proceed in ['yes', 'no']:
                    if proceed == 'yes':
                        habit_objects.remove(habit)  # Delete the existing habit
                        print(f"\nThe habit '{habit.name}' has been deleted.")
                    return proceed == 'yes'
                else:
                    FileManager.logger.warning("Invalid input. Expected 'yes' or 'no'.")
                    print("Invalid input. Please type 'yes' or 'no'.")
    return True


def edit_habit(habit: Habit) -> None:
    """Allows the user to edit the habit's information."""
    options = {
        1: "Name",
        2: "Periodicity",
        3: "Decoration",
        4: "Delete this habit"
    }

    print("\nWhat would you like to change?")
    for key, value in options.items():
        print(f"{key}. {value}")

    choice = choice_check(len(options))

    if choice == 1:
        habit.name = get_habit_name()
        print(f"\nThe name of the habit has been updated to '{habit.name}'!")

    elif choice == 2:
        habit.periodicity = get_periodicity()
        habit.next_completion_date = habit.calculate_completion_date()
        habit.fails = 0
        habit.streak = 0
        habit.longest_streak = 0
        print(f"\nAfter changing periodicity, your fails and streaks are now set to 0!"
              f"\nYour new next completion date is {habit.formatted_date}.")

    elif choice == 3:
        habit.reset_decoration()
        print("\nPlease enter the number of the decoration you're interested in.")
        if giving_list(decor_objects):
            decoration_choice = choice_check(len(decor_objects))
            decoration = decor_objects[decoration_choice - 1]
            if decor_check(decoration, habit_objects, current_habit=habit):
                habit.decoration = decoration
                habit.decoration.exp = 0  # Reset the new decoration's EXP
                print(f"\nDecoration for habit '{habit.name}' has been updated, EXP reset to 0!")
            else:
                print("\nDecoration change canceled.")

    elif choice == 4:
        habit.reset_decoration()
        habit_objects.remove(habit)
        print(f"This habit '{habit.name}' was deleted!")

    saving()
    type_ok()


def delete_habits():
    """Deletes all current habits, clearing the habit_objects list."""
    global habit_objects  # Ensure we're modifying the global habit_objects list
    for habit in habit_objects:
        habit.reset_decoration()  # Reset decorations before deleting habits
    habit_objects = []  # Clear the list
    wrapped_message("All habits and their linked decorations have been deleted and reset!", 70)
    saving()  # Save the updated (empty) list to the JSON file
    return

def handle_check_in():
    """Handle the check-in process for habits."""
    if empty_list(habit_objects):
        return

    wrapped_message("LET'S CHECK IN!", 30)
    if len(habit_objects) == 1:
        # If there's only one habit, automatically start check-in
        habit_objects[0].check_in()
    else:
        # If there's more than one habit, display the habits and ask for choice
        view_items(habit_objects, Habit.habit_criteria_map, is_habit=True, action="check_in")

    saving()


def quotes_and_tips() -> (str, str):
    """
    Retrieves a random motivational quote and tip.

    Returns:
        tuple: A random quote and a random tip.
    """
    random_quote = random.choice(quotes) if quotes else "\nNo quotes today. :("
    random_tip = random.choice(tips) if tips else "\nNo tips today. :("
    return random_quote, random_tip


def butler_menu():
    """Display the butler menu with options to view, hire, or talk to the butler."""
    global butler

    # If no Butler exists, generate a new one
    if not butler:
        wrapped_message("Looks like your Butler went missing! "
                        "Keep calm, the Agency is sending a new one...", 80)
        butler = Butler.generate_butler(butler_options)

    while True:
        wrapped_message("THE BUTLER IS HERE!", 30)
        print("They will help you learn more about your progress.")

        print("What would you like to do?"
              "\n\n== YOUR BUTLER =="
              "\n1. About them"
              "\n2. Chit-chat"
              "\n3. Hire a new one"
              "\n\n== YOUR PROGRESS =="
              "\n4. Ask about my progress"
              "\n5. Get a motivational quote and a tip"
              "\n6. Go back")
        choice = choice_check(6)

        if choice == 1:
            butler.display_info()
        elif choice == 2:
            butler.talk_to(butler_options)
        elif choice == 3:
            wrapped_message("You fired the previous Butler! The Agency sent you a new one.", 70)
            butler = Butler.generate_butler(butler_options)
        elif choice == 4:
            butler.provide_analytics(habit_objects)
        elif choice == 5:
            random_quote, random_tip = quotes_and_tips()
            wrapped_message(f"MOTIVATIONAL QUOTE: {random_quote} \nTIP OF THE DAY: {random_tip}", 100)
            type_ok()
        elif choice == 6:
            break


def main_menu():
    """Display the main menu and handle user navigation."""
    while True:
        wrapped_message("MAIN MENU", 50)
        print("Please type valid numbers to navigate the app."
              "\nType X at any point to return back to the main menu.")
        print("\n== HABITS =="
              "\n1. Check-in!"
              "\n2. Create a new habit"
              "\n3. View all your habits"
              "\n4. Delete all your habits"
              "\n\n== PALACE =="
              "\n5. Check the palace's rooms"
              "\n6. Check decorations"
              "\n\n== BUTLER =="
              "\n7. Talk to the Butler"
              "\n\n== OTHER =="
              "\n8. Exit the app")
        choice = choice_check(8)

        if choice == 1:
            handle_check_in()
        elif choice == 2:
            create_new_habit()
        elif choice == 3:
            if habit_objects:
                wrapped_message("Here's a list of your habits:", 55)
            view_items(habit_objects, Habit.habit_criteria_map, is_habit=True)
        elif choice == 4:
            delete_habits()
            type_ok()
        elif choice == 5:
            wrapped_message("Here's a list of all the rooms in your palace:", 50)
            giving_list(Conversion.rooms)
            type_ok()
        elif choice == 6:
            wrapped_message("Here's a list of your decorations:", 55)
            view_items(decor_objects, Decoration.decor_criteria_map, is_habit=False)
        elif choice == 7:
            butler_menu()
        elif choice == 8:
            saving()
            exit()


# Initialize lists to keep track of corrupted data and fails
corrupted_data = []
failed_habits = []

# Load and convert data
decor_objects = [Conversion.convert_decor(decor) for decor in FileManager.load_data('decorations.json')]
habit_objects = [Conversion.convert_habit(habit, decor_objects) for habit in FileManager.load_data('habits.json')]

# Load Butler data
butler_options = FileManager.load_data('butler_options.json')
current_butler_data = FileManager.load_data('current_butler.json')
tips = FileManager.load_data('tips.json')
quotes = FileManager.load_data('quotes.json')

# Initialize Butler object
butler = None
if current_butler_data:
    if isinstance(current_butler_data, list) and len(current_butler_data) > 0:
        current_butler_data = current_butler_data[0]  # Take the first element if it's a list
    if isinstance(current_butler_data, dict):
        butler = Butler(**current_butler_data)
    else:
        butler = None  # No Butler yet
else:
    butler = None  # No Butler yet

# Check for failed habits only if the current time is past the end of the check-in day
for habit in habit_objects:
    original_fails = habit.fails
    completion_date_end = habit.next_completion_date.replace(hour=23, minute=59, second=59)

    # Only mark as failed if current time is past the end of the allowed check-in time
    if datetime.now() > completion_date_end:
        if habit.calculate_fails() and habit.fails > original_fails:
            failed_habits.append(habit)

            # Deduct EXP for each fail
            for _ in range(habit.fails - original_fails):  # Deduct for each new fail
                deduction = habit.exp_values.get(habit.periodicity, 0) / 2
                habit.decoration.exp = max(habit.decoration.exp - deduction, 0)
                habit.decoration.update_state()  # Update the decoration state after deduction

# Start the app
print("\nWelcome to the Habit Tracker!")

if corrupted_data:
    wrapped_message("Unfortunately, some data was corrupted. We had to change certain habits/decorations."
          "\nHere are the changes: ", 50)
    giving_list(corrupted_data)

if failed_habits:
    wrapped_message("Unfortunately, you failed the following habits since the last time: ", 50)
    giving_list(failed_habits)
    print("\nDon't get upset. You got this!")
    type_ok()

main_menu()
saving()
