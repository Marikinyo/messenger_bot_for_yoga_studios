# import os
# import json
# from config import data_folder

# # Automatically find the project root (where this file lives)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, data_folder)

# def load_data_from_file(filename: str):
#     """Loads a JSON file from the data directory and returns the data."""
#     filepath = os.path.join(DATA_DIR, filename)
#     try:
#         with open(filepath, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: The file '{filepath}' was not found. Please create it.")
#         return {}
#     except json.JSONDecodeError:
#         print(f"Error: The file '{filepath}' contains invalid JSON. Please check the file format.")
#         return {}


import os
import json
from config import data_folder
from typing import Dict, Any

# Automatically find the project root (where this file lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR is the root 'data' folder
DATA_DIR = os.path.join(BASE_DIR, data_folder)

def load_data_from_file(filename: str, page_id: str) -> Dict[str, Any]:
    """
    Loads a JSON file from the data directory's specific page subfolder.
    It attempts to find the correct subfolder that STARTS with the page_id.
    
    Args:
        filename (str): The name of the file (e.g., 'faq_english.json').
        page_id (str): The ID of the Facebook page (e.g., '1234').

    Returns:
        Dict[str, Any]: The loaded JSON data, or an empty dictionary on error.
    """
    
    # 1. Search for the actual folder name (e.g., '1234_TestPage')
    # We iterate over everything inside the DATA_DIR to find a match.
    page_folder_name = None
    
    # List all entries in the data directory
    for item in os.listdir(DATA_DIR):
        # Check if the item is a directory AND if its name starts with the page_id
        if os.path.isdir(os.path.join(DATA_DIR, item)) and item.startswith(page_id + '_'):
            page_folder_name = item
            break # Found the correct folder, stop searching
            
    if not page_folder_name:
        print(f"Error: Data folder for Page ID '{page_id}' (starting with {page_id}_) was not found in {DATA_DIR}.")
        return {}

    # 2. Construct the path to the page's subfolder (e.g., 'data/1234_TestPage')
    page_folder_path = os.path.join(DATA_DIR, page_folder_name)
    
    # 3. Construct the full file path (e.g., 'data/1234_TestPage/faq_english.json')
    filepath = os.path.join(page_folder_path, filename)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found in the expected page folder: {page_folder_path}")
        return {}
        
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' contains invalid JSON. Please check the file format.")
        return {}

    