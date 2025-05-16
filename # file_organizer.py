file_organizer.py

import os
import pathlib
import shutil
import csv
from datetime import datetime

# --- Configuration ---

# Directory to scan for files to organize
# Example: pathlib.Path.home() / "Downloads"
SOURCE_DIR = pathlib.Path(r"C:\Users\UserName\Desktop\ToSort") # <--- CHANGE THIS to your source folder

# Directory where organized folders will be created
# Example: pathlib.Path.home() / "Organized Files"
DEST_DIR = pathlib.Path(r"C:\Users\UserName\Desktop\Organized") # <--- CHANGE THIS to your destination folder

# Path for the CSV log file
LOG_FILE = DEST_DIR / "organization_log.csv"

# Mapping of file extensions (lowercase) to folder names
# Add more extensions and categories as needed
FILE_TYPE_MAPPINGS = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".tiff": "Images",
    ".svg": "Images",
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets", # Note: Don't run this IN the DEST_DIR if you name your log .csv!
    ".ppt": "Presentations",
    ".pptx": "Presentations",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".flac": "Audio",
    # Video
    ".mp4": "Video",
    ".mov": "Video",
    ".avi": "Video",
    ".mkv": "Video",
    # Code/Scripts
    ".py": "Scripts",
    ".js": "Scripts",
    ".html": "Web",
    ".css": "Web",
    # Executables/Installers
    ".exe": "Executables",
    ".msi": "Executables",
    # Add more mappings here...
}

# Name for the folder if the file type is not in the mappings
OTHER_FOLDER_NAME = "Others"

# --- Functions ---

def setup_logging():
    """Creates the destination directory and initializes the CSV log file if needed."""
    DEST_DIR.mkdir(parents=True, exist_ok=True) # Create destination if it doesn't exist
    if not LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Original Path", "New Path", "File Type"])
            print(f"Created log file: {LOG_FILE}")
        except IOError as e:
            print(f"Error creating log file {LOG_FILE}: {e}")
            return False
    return True

def log_action(original_path, new_path, file_type):
    """Appends a record to the CSV log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, str(original_path), str(new_path), file_type])
    except IOError as e:
        print(f"Error writing to log file {LOG_FILE}: {e}")
    except Exception as e:
         print(f"An unexpected error occurred during logging: {e}")

def organize_files():
    """Scans the source directory and moves files to the destination directory."""
    print(f"Scanning source directory: {SOURCE_DIR}")
    print(f"Organizing into destination: {DEST_DIR}")
    print("-" * 30)

    if not SOURCE_DIR.is_dir():
        print(f"Error: Source directory '{SOURCE_DIR}' not found or is not a directory.")
        return

    moved_count = 0
    skipped_count = 0

    for item in SOURCE_DIR.iterdir():
        if item.is_file():
            original_path = item
            file_extension = original_path.suffix.lower() # Get extension like '.txt'

            # Determine target folder name
            target_folder_name = FILE_TYPE_MAPPINGS.get(file_extension, OTHER_FOLDER_NAME)
            target_subdir = DEST_DIR / target_folder_name

            # Create target subdirectory if it doesn't exist
            target_subdir.mkdir(parents=True, exist_ok=True)

            # Construct the full destination path
            new_path = target_subdir / original_path.name

            # Avoid overwriting: Check if file already exists in destination
            if new_path.exists():
                print(f"Skipping '{original_path.name}': File already exists in '{target_folder_name}'.")
                skipped_count += 1
                continue

            # Move the file
            try:
                shutil.move(str(original_path), str(new_path))
                print(f"Moved '{original_path.name}' -> '{target_folder_name}/'")
                # Log the action
                log_action(original_path, new_path, target_folder_name)
                moved_count += 1
            except OSError as e:
                print(f"Error moving '{original_path.name}': {e}")
                skipped_count += 1
            except Exception as e:
                 print(f"An unexpected error occurred moving '{original_path.name}': {e}")
                 skipped_count += 1
        # else: # Optional: Handle directories found in the source directory
        #     print(f"Skipping directory: {item.name}")
        #     skipped_count += 1

    print("-" * 30)
    print("Organization complete.")
    print(f"Files moved: {moved_count}")
    print(f"Files skipped: {skipped_count}")
    if moved_count > 0:
        print(f"Details logged in: {LOG_FILE}")

# --- Main Execution ---

if __name__ == "__main__":
    # Ensure paths are absolute for clarity, though pathlib handles relative paths too
    SOURCE_DIR = SOURCE_DIR.resolve()
    DEST_DIR = DEST_DIR.resolve()
    LOG_FILE = LOG_FILE.resolve() # Resolve log file path based on potentially resolved DEST_DIR

    # Basic check to prevent organizing the destination into itself if paths overlap carelessly
    if SOURCE_DIR == DEST_DIR or DEST_DIR.is_relative_to(SOURCE_DIR):
         print(f"Error: Destination directory '{DEST_DIR}' cannot be the same as or inside the source directory '{SOURCE_DIR}'.")
    elif setup_logging():
        organize_files()
    else:
        print("Setup failed. Exiting.")

