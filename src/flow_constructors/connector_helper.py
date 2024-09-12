import datetime
import glob
import json
import os
import random
import shutil
import subprocess
import time
import calendar
import uuid
import piexif
from src.flow_constructors.allure_log import print_log


class Connector:
    file_names = None
    file_name = None
    config_override_file = {}

    def __init__(self, application_parameters, photo_upload_path, video_upload_path, photo_source_path,
                 video_source_path, connector_main_path, uploads_path, video_path, photo_path):
        self.application_parameters = application_parameters
        self.photo_upload_path = photo_upload_path
        self.video_upload_path = video_upload_path
        self.photo_source_path = photo_source_path
        self.video_source_path = video_source_path
        self.connector_main_path = connector_main_path
        self.uploads_path = uploads_path
        self.video_path = video_path
        self.photo_path = photo_path

    @staticmethod
    def get_connector_main_path():

        return glob.glob(r'C:\connector')[0]

    @staticmethod
    def get_uploads_path(connector_main_path):
        print_log(f"get_uploads_path: {connector_main_path} + \\uploads", connector_main_path + " \\uploads")
        return connector_main_path + "\\uploads"

    @staticmethod
    def get_video_path(connector_main_path, media_path):
        print_log(f"get_video_path: {media_path}", connector_main_path + str(media_path))
        return connector_main_path + media_path

    @staticmethod
    def get_photo_path(connector_main_path, media_path):
        print_log(f"get_video_path: {media_path}", connector_main_path + str(media_path))
        return connector_main_path + media_path

    def edit_config_file(self):
        # Open file
        file = open(str(self.connector_main_path) + "\\configOverride.json")
        Connector.config_override_file = json.load(file)

        utc_time_now = datetime.datetime.now(datetime.UTC)
        timestamp_milliseconds = calendar.timegm(utc_time_now.timetuple() * 1000) * 1000

        print("UTC time_new in real time: " + str(utc_time_now))
        print("timestamp_milliseconds: " + str(timestamp_milliseconds))

        # Change values in Connector config
        Connector.config_override_file['siteCode'] = self.application_parameters['site_code'].upper()
        Connector.config_override_file['attractionCode'] = self.application_parameters['attraction'].upper()
        Connector.config_override_file['regionGCP'] = self.application_parameters['environment']
        Connector.config_override_file['forcedCreateTime'] = timestamp_milliseconds
        # Connector.config_override_file['jpgOffset'] = 0
        Connector.config_override_file['verboseUploads'] = False

        # Convert config to JSON string with new lines after commas
        config_json_str = json.dumps(Connector.config_override_file, separators=(',', ': ')).replace(',', ',\n')

        # Write / Create a new configOverride.json file
        with open(str(self.connector_main_path) + "\\configOverride.json", "w") as outfile:
            outfile.write(config_json_str)
            # json.dump(Connector.config_override_file, outfile)

        # Config - Print
        print("Print Config after edit:")
        print(Connector.config_override_file)

    def run_connector(self, time_out):
        try:
            # Openning connector.exe file
            filepath = glob.glob(r'C:\connector\Picasso_Connector.exe')[0]
            print_log(f"file path of Picasso_Connector: {filepath}", "file path is: " + str(filepath))

            # os.system(filepath)
            subprocess.run(filepath, cwd=self.connector_main_path, timeout=time_out)

            #####
            # Define the command to run
            filepath = glob.glob(r'C:\connector\Picasso_Connector.exe')[0]

            # Define the path to the log file
            log_path = r'C:\connector\logfile.txt'

            # Run the command and capture the output and error streams to the log file
            with open(log_path, 'w') as log_file:
                subprocess.run(filepath, cwd=glob.glob(r'C:\connector')[0], timeout=time_out, stdout=log_file,
                               stderr=log_file)

            #####

        except subprocess.TimeoutExpired:
            print_log("Media uploaded successfully", " ")
            print_log(f"Time out for connector to shut down: {time_out} seconds", "Time out was %s seconds" % time_out)

        time.sleep(30)

    def renaming_uuid_in_photo_files(self, uuid_assignment, origin_uuid=None):
        print("\nUUID PHOTO Rename start \n")
        # List of file names
        file_names = os.listdir(self.photo_path)
        print("origin_uuid for photos: " + str(origin_uuid))
        # For totr domain
        if uuid_assignment == "all_files_same_uuid":
            for file_name in file_names:
                file_path = os.path.join(self.photo_path, file_name)
                if file_name.endswith((".jpg", ".png")):
                    self.change_image_uuid(file_path, origin_uuid)
                else:
                    pass

        # Rest of test
        if uuid_assignment == "jpg_pairs":
            # Create a dictionary to store all the file names with the same number
            file_num_dict = {}
            for file_name in file_names:
                if file_name.endswith(".mp4"):
                    continue

                file_num = file_name.split("-")[5]

                if file_num not in file_num_dict:
                    file_num_dict[file_num] = []
                file_num_dict[file_num].append(file_name)

            # Iterate through the dictionary and update the UUID for all the matching files
            for file_num, file_names in file_num_dict.items():
                # Print for logs
                print("file_number: " + str(file_num))
                print("file_names: " + str(file_names))
                if len(file_names) < 2:
                    continue

                # Generate originUUID for all matching files
                originUUID = uuid.uuid1()
                print("originUUID: " + str(originUUID))

                # Update the UUID for all matching JPG files using exif
                for file_name in file_names:
                    self.change_image_uuid(os.path.join(self.photo_path, file_name), originUUID)

        print("\nUUID PHOTO Rename ended \n")

    def renaming_uuid_in_video_files(self, uuid_assignment, origin_uuid,  ai_meta_data_video=None):
        # For the use of dq domain
        print("origin_uuid in new_renaming_uuid_in_video_files: " + str(origin_uuid))
        print("\nUUID VIDEO Rename start \n")
        file_names = os.listdir(self.photo_path)

        for file_name in file_names:
            file_path = os.path.join(self.photo_path, file_name)
            if file_name.endswith(".mp4") and uuid_assignment == "pre_association_in_meta_data":
                self.change_video_uuid(file_path, origin_uuid, pre_association=ai_meta_data_video)
            if file_name.endswith(".mp4") and uuid_assignment == "origin_uuid_in_meta_data":
                self.change_video_uuid(file_path, origin_uuid)


        print("\nUUID VIDEO Rename ended \n")

    def photos_drag_and_drop_and_upload(self, attraction_names):

        target_dir = self.uploads_path
        source_dir = self.photo_path

        try:
            # List of file names
            file_names = os.listdir(source_dir)

            # Create a dictionary that maps each number to a list of file names that contain that number
            file_dict = {}

            # if Connector.file_name.endswith(".jpg"):
            for Connector.file_name in file_names:
                # only photo
                if Connector.file_name.endswith(".jpg"):
                    number = Connector.file_name.split("-")[5]
                    if ".jpg" in number:
                        number_parts = number.split(".")
                        only_number = number_parts[0]
                        number = only_number
                    else:
                        pass

                    if number not in file_dict:
                        file_dict[number] = []
                    file_dict[number].append(Connector.file_name)

            print("file dictionary of all 'jpg' files: " + str(file_dict))

            # Extract only file names out of the dictionary
            for number in file_dict.keys():
                file_names_for_number = file_dict[number]
                print("old_file_names: " + str(file_names_for_number))

                new_numbers = []  # Initialize an empty list to store new_number values for print_log only

                new_number = "0" + str(random.randint(1000, 9999))

                attraction_names_cycle = [attraction_names[i % 2] for i in range(len(file_names))]

                # For loop, runs on all attractions, starts at '0', and jumps +2 cells each time (i.e - 1st cycle is : [0,1] )
                for i in range(0, len(file_names_for_number), 2):

                    # For loop, handling 2 cells each time, from i till i+2 (cell +2 is ignored!) && using camera Id index
                    for file_name_list_index, attraction_name in zip(range(i, min(i + 2, len(file_names_for_number))),
                                                                     attraction_names_cycle[i:i + 2]):
                        try:
                            # File rename, for PHOTO
                            print("\nPhoto Rename start \n")
                            print("File Number %s - Starting handling START " % str(file_name_list_index))
                            print("Before change - file name was: " + str(file_names_for_number[file_name_list_index]))
                            modified_photo_file_name = self.change_photo_file_name_media_testing(
                                file_names_for_number[file_name_list_index], new_number)
                            print("After change - file name is: " + modified_photo_file_name)
                            print("\nPhoto Rename finished \n")
                            shutil.copy(os.path.join(source_dir, modified_photo_file_name), target_dir)
                        except (FileNotFoundError, PermissionError) as e:
                            print_log("File processing error",
                                f"An error occurred while processing file {file_names_for_number[file_name_list_index]}: {e}")

                        new_numbers.append(new_number)  # Append new_number to the list

                print_log("new file names numbers", "new file names numbers: " + str(new_numbers))

            print_log("All photos renamed", "----------------------------------------------------- All photos renamed and copy to upload folder --------------------------------------------------------------")

        except (FileNotFoundError, PermissionError) as e:
            print_log("Source directory error", f"An error occurred while accessing the source directory {source_dir}: {e}")

    def video_drag_and_drop_and_upload(self):
        target_dir = self.uploads_path
        source_dir = self.photo_path

        try:
            # List of file names
            file_names = os.listdir(source_dir)

            for Connector.file_name in file_names:
                # only Video
                if Connector.file_name.endswith(".mp4"):
                    try:
                        new_number = "0" + str(random.randint(1000, 9999))
                        # File rename, for VIDEO
                        print("\nVideo Rename start \n")
                        print("Before change - file name was : " + str(Connector.file_name))
                        modified_video_file_name = self.change_video_file_name_media_testing(
                            Connector.file_name, new_number)
                        print("After change - file name was: " + modified_video_file_name)
                        print("\nVideo Rename finished \n")
                        shutil.copy(os.path.join(source_dir, modified_video_file_name), target_dir)
                    except (FileNotFoundError, PermissionError) as e:
                        print_log("File processing error", f"An error occurred while processing file {Connector.file_name}: {e}")

        except (FileNotFoundError, PermissionError) as e:
            print_log("Source directory error", f"An error occurred while accessing the source directory {source_dir}: {e}")

    def change_video_file_name_media_testing(self, file_name, new_number):
        # Rename date video file for this structure '2023-02-20-LF-DV-TWI-00020-002'
        # Extract original file date components
        parts = file_name.split("-")
        date = parts[0] + "-" + parts[1] + "-" + parts[2]
        number = parts[6]

        # Generate a new date in the format of YYYY-MM-DD
        new_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        # Replace the date portion of the file name with the new date
        new_file_name = file_name.replace(date, new_date).replace(number, new_number)
        print("old file name: " + str(file_name))
        print("new_file_name: " + str(new_file_name))
        os.rename(self.video_path + "\\" + file_name,
                  self.video_path + "\\" + new_file_name)

        return self.video_path + "\\" + new_file_name

    def change_photo_file_name_media_testing(self, file_name, new_number):
        while len(file_name) > 0:
            print("new_number: " + str(new_number))
            # Rename date photo file for this structure '2023-02-20-LF-DV-00150-0012'
            # Extract original file date components
            parts = file_name.split("-")
            print("parts: " + str(parts))
            date = parts[0] + "-" + parts[1] + "-" + parts[2]
            # Generate a new date in the format of YYYY-MM-DD
            new_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

            number = parts[5]
            print("number: " + str(number))
            if ".jpg" in number:
                number_parts = number.split(".")
                only_number = number_parts[0]
                number = only_number
                print("number in if: " + str(number))
            else:
                pass

            print("new_number: " + str(new_number))
            # Replace the date portion of the file name with the new date and the number
            new_file_name = file_name.replace(date, new_date).replace(number, new_number)

            os.rename(self.photo_path + "\\" + file_name,
                      self.photo_path + "\\" + new_file_name)

            return self.photo_path + "\\" + new_file_name

    @staticmethod
    def change_image_uuid(file_path, origin_uuid):
        # Load the exif data from the image
        exif_dict = piexif.load(file_path)

        # Update the author field (using the tag ID)
        exif_dict["0th"][315] = str(origin_uuid)

        # Save the updated exif data back to the image
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)

    @staticmethod
    def change_video_uuid(file_path, uuid_value=None, create_time=None, pre_association=None):
        file_directory, file_name = os.path.split(file_path)

        modified_number = "0" + str(random.randint(1000, 9999))
        file_name_split = file_name.split("-")
        file_name_split[6] = modified_number
        output_file_name = "-".join(file_name_split)

        full_file_output_path = os.path.join(file_directory, output_file_name)

        command = [
            r"C:\connector\ffmpeg.exe",
            "-i", file_path,
            "-codec", "copy",
            "-movflags", "use_metadata_tags",
            "-metadata", f"createTime={create_time}" if create_time is not None else "createTime=",
            "-metadata", "originUUID="f"{uuid_value}" if uuid_value is not None else "originUUID=",
            "-metadata", f"preAssociation={pre_association}" if pre_association is not None else "preAssociation=",
            full_file_output_path
        ]
        print("command: " + str(command))

        try:
            # Run FFmpeg command
            subprocess.run(command, check=True)

            # Delete the input video file
            os.remove(file_path)

            print(f"FFmpeg command executed successfully. Input file deleted.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing FFmpeg command: {e}")

    @staticmethod
    def get_origin_uuids(folder_path):
        uuids = set()
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jpg"):
                file_path = os.path.join(folder_path, file_name)
                exif_dict = piexif.load(file_path)
                uuid_bytes = exif_dict["0th"].get(315)
                if uuid_bytes is not None:
                    uuid_str = uuid_bytes.decode('utf-8')
                    uuids.add(uuid_str)
        return uuids

