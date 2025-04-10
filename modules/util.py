import os
from dotenv import load_dotenv
import logging

def get_secret(key, FILE_PATH="", default=None):
    """
    Retrieves the value of a specified environment variable from a .env file.

    Args:
        key (str): The name of the environment variable to retrieve.
        FILE_PATH (str, optional): The file path to the .env file. Defaults to an empty string.

    Returns:
        str or None: The value of the environment variable if found, otherwise None.

    Raises:
        Exception: If the key is not found or its value is None.
    """

    try:
        load_dotenv(FILE_PATH)
        value = os.getenv(key)
        if value == None:
            #throw error if key not found
            logging.debug(f"Key {key} not found / is None")
        return value
    except Exception as e:
        logging.error(f"Get_secret() Error getting secret from {FILE_PATH}: {key}: {e}")
        return default