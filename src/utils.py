import json
import logging

logger = logging.getLogger()

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"{file_path} not found.")
        return {}
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return {}

def write_json_file(data, file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Failed to write to {file_path}: {e}")
