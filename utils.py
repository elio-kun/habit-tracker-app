import builtins
from typing import List, Dict, Any, Callable
from file_manager import FileManager

def type_ok():
    """Prompts the user to type 'OK' to continue."""
    while True:
        choice = input("\nType 'OK' to continue: ").strip().upper()
        if choice == "OK":
            break
        else:
            print("\nDude, come on. Type OK to continue.")


def wrapped_message(message: str, width: int = 30):
    """Prints a message wrapped in lines of '='."""
    print("\n" + "=" * width)
    print(message.center(width))  # Center the message within the wrapper
    print("=" * width)


def get_day_with_suffix(day: int) -> str:
    """Returns the day of the month with the appropriate suffix."""
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"


def choice_check(number: int) -> int:
    """Prompt the user to enter a valid number within a specified range."""
    while True:
        try:
            choice = int(input(f"\nPlease enter a number between 1 and {number}: "))
            if 1 <= choice <= number:
                return choice
            else:
                FileManager.logger.warning(f"Invalid input: {choice}. Expected a number between 1 and {number}.")
                print(f"\nInvalid input. Please enter a number between 1 and {number}.")
        except ValueError:
            FileManager.logger.warning(f"Invalid input. Expected a number between 1 and {number}.")
            print(f"Invalid input. Please enter a number between 1 and {number}.")


def empty_list(current_list: List[Any]) -> bool:
    """Check if the list is empty and print a message if it is."""
    if not current_list:
        wrapped_message("Sorry, but this list is empty! Returning...", 50)
        return True
    return False