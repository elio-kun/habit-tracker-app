import json
import logging
from typing import List, Dict, Any

class FileManager:
    """Handles file operations like loading and saving JSON data."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    @staticmethod
    def load_data(filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            filename (str): The name of the JSON file to load.

        Returns:
            List[Dict[str, Any]]: The data loaded from the JSON file, or an empty list if an error occurs.
        """
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                FileManager.logger.info(f"Loaded data from {filename}")
                return data
        except FileNotFoundError:
            FileManager.logger.error(f"{filename} not found.")
            return []
        except json.JSONDecodeError as e:
            FileManager.logger.error(f"Error reading {filename}: {e}")
            return []

    @staticmethod
    def save_data(filename: str, data: List[Dict[str, Any]]):
        """
        Save data to a JSON file.

        Args:
            filename (str): The name of the JSON file to save.
            data (List[Dict[str, Any]]): The data to save.
        """
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
                FileManager.logger.info(f"Saved data to {filename}")
        except IOError as e:
            FileManager.logger.error(f"Error writing to {filename}: {e}")