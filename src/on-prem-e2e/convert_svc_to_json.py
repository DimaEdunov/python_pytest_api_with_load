import os
import json
import csv
from datetime import datetime


def convert_csv_to_json(csv_path):
    # Read the CSV file content
    with open(csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_list = list(reader)

    return csv_list


def save_json(json_data, json_path):
    with open(json_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=3)


def retain_file_dates(src_path, dst_path):
    stat = os.stat(src_path)
    os.utime(dst_path, (stat.st_atime, stat.st_mtime))


def main(directory):
    os.chdir(directory)

    for filename in os.listdir():
        print("XXX in for main")
        if filename.endswith('.csv'):
            csv_path = os.path.join(directory, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(directory, json_filename)

            # Convert CSV to JSON
            json_data = convert_csv_to_json(csv_path)

            # Save JSON to file
            save_json(json_data, json_path)

            # Retain the same date for the JSON file
            retain_file_dates(csv_path, json_path)

            # Delete the CSV file
            os.remove(csv_path)

if __name__ == "__main__":
    folder_path = 'C:\\connector\\test_update_json_file'
    main(folder_path)
