import os
import shutil
import time
import uuid
import piexif


class ScreamLoadTest:
    # Load testing os scream AI model. The scream operates in tp park.
    # This script takes 1 photo multiply it by 3 with the right file manes, and cope it to the right folder
    def __init__(self, photo_path):
        self.photo_path = photo_path

    def generate_file_names(self, base_filename, common_number):
        extensions = ["ST", "SV", "VS"]
        number_part = f"{common_number:05d}"

        for ext in extensions:
            yield f"{base_filename}-{ext}-{number_part}-001"

    def copy_and_rename_files(self):
        if not os.path.exists(self.photo_path):
            print(f"Folder '{self.photo_path}' does not exist.")
            return

        file_list = [f for f in os.listdir(self.photo_path) if f.endswith('.jpg')]
        file_count = len(file_list)

        if file_count == 0:
            print("No JPG files found in the folder.")
            return

        destination_root = os.path.join(self.photo_path, "destination")
        os.makedirs(destination_root, exist_ok=True)

        print(f"Copying and renaming {file_count} files...")

        for common_number, filename in enumerate(file_list, start=144):
            source_file = os.path.join(self.photo_path, filename)
            base_name = f"2023-08-31-TP"

            set_folder = os.path.join(destination_root, f"Set_{common_number:05d}")
            os.makedirs(set_folder, exist_ok=True)

            print(f"\nProcessing file '{filename}'...")

            for j, new_filename in enumerate(self.generate_file_names(base_name, common_number)):
                destination_file = os.path.join(set_folder, new_filename + ".jpg")
                shutil.copyfile(source_file, destination_file)
                print(f"  Copied to '{destination_file}'")

            print(f"  Set folder '{set_folder}' created.")

            # Add UUID to all images in the set
            self.add_uuid_to_images_in_folder(set_folder)

            # Move the image files to the destination with sleep time
            self.move_image_files_to_destination(set_folder)
            time.sleep(20)  # Wait for 60 seconds before the next iteration

        print("\nCopying, renaming, adding UUIDs, and moving image files completed.\n")

    def add_uuid_to_images_in_folder(self, folder_path):
        origin_uuid = uuid.uuid1()
        print(f"  Adding UUID {origin_uuid} to images in '{folder_path}'...")
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg'):
                image_path = os.path.join(folder_path, filename)
                self.change_jpg_file_uuid(image_path, origin_uuid)

    @staticmethod
    def change_jpg_file_uuid(file_path, origin_uuid):
        # Load the exif data from the image
        exif_dict = piexif.load(file_path)

        # Update the author field (using the tag ID)
        exif_dict["0th"][315] = str(origin_uuid)

        # Save the updated exif data back to the image
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
        print(f"  Added UUID {origin_uuid} to '{file_path}'")

    def move_image_files_to_destination(self, set_folder):
        for filename in os.listdir(set_folder):
            if filename.endswith('.jpg'):
                image_path = os.path.join(set_folder, filename)
                destination_path = os.path.join("c:\\connector\\Uploads", filename)
                shutil.move(image_path, destination_path)
                print(f"  Moved '{filename}' to 'c:\\connector\\Uploads'")


if __name__ == "__main__":
    folder_path = "C:\\TP-photos\\Right_folder"
    processor = ScreamLoadTest(folder_path)
    processor.copy_and_rename_files()
