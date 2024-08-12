# Habit Tracker
# Overview
Habit Tracker is a Python-based app designed to help users track and analyze their habits over time. The users renovate an old, dusty palace by tracking their habits. As users successfully track their habits, the palace's decorations gain experience points (EXP) and transform, leading to the complete renovation of the palace.

# Features
- **Mind Palace:** Choose decorations for each habit, and as you track your progress, the decorations gain EXP and upgrade from "Old" to "Great", helping to renovate the palace.
- **Habit Management:** Create, edit, and delete habits with associated decorations.
- **Progress and Analytics:** Track your current and longest streaks and fails for each habit.
- **Butler Assistant:** An in-app assistant provides analytics, motivation, and guidance on your progress.
- **CLI Navigation:** The app is operated through a Command-Line Interface (CLI), where you can navigate using numbers/keys.

# Project Structure
The project is organized into several key directories:

- **src/:** Contains the main code.
   - **__main__.py:** The entry point of the app.
   - **analytics.py:** Functional programming module for habit analysis.
   - **conversion.py:** Handles conversion between JSON data and Python objects.
   - **file_manager.py:** Manages file operations like loading and saving JSON data.
   - **models.py:** Contains the Habit, Decoration, and Butler classes.
   - **utils.py:** Utility functions used across the project.
- **data/:** Stores JSON files with predefined data and user progress.
   - **butler_options.json:** Options for generating Butler characters.
   - **current_butler.json:** Stores the current Butler's data.
   - **decorations.json:** Stores predefined decorations.
   - **habits.json:** Stores user habits.
   - **quotes.json:** Stores motivational quotes.
   - **tips.json:** Stores tips provided by the Butler.
- **tests/:** Contains unit tests for the project.
   - predefined_habits.json: Predefined habit data used for testing.
   - test_habits.py: Unit tests for the habit tracking and analytics functionality.
.gitignore: Specifies files and directories to be ignored by Git.

## Installation

1. **Clone the repository:**

   ``git clone https://github.com/elio-kun/habit-tracker-app.git``

   ``cd habit-tracker``

3. **Run the application:**
   Navigate to the 'src' directory and run the __main__.py script:

   ``cd src``

   ``python __main__.py``

## Usage
- **Navigate the App:** Enter numbers corresponding to available options. Follow the prompts to move through menus and select actions.
- **Create a Habit:** Start by creating a new habit. Follow the on-screen prompts to select a decoration, name the habit, and choose its periodicity.
- **Check In:** Track your habit daily, weekly, monthly, or yearly as specified. Successfully tracking a habit adds EXP to its decoration and updates its state.
- **Talk to the Butler:** Use the Butler to chit-chat with, get inspiration, and analyze your progress by running the provide_analytics method.

## Testing
The project includes a suite of unit tests to ensure that the critical functionalities work as expected. To run the tests:

``cd tests``

``python -m unittest test_habits.py``

## Contributing
If you’d like to contribute to this project, please fork the repository and create a pull request. All improvements and bug fixes are welcome.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
