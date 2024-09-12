import os
import subprocess

source_dir = 'C:\\Background-removal\\room_on_the_broom_source'
output_dir = 'C:\\Background-removal\\room_on_the_broom_result2'

# Path to the executable
exe_path = 'C:\\bGoneLite_0.1.0\\bGoneLite.exe'

# Iterate through each jpg file in the source directory
for filename in os.listdir(source_dir):
    if filename.lower().endswith('.jpg'):
        source_file = os.path.join(source_dir, filename)
        output_file = os.path.join(output_dir, filename)

        # Construct and run the command
        cmd = [exe_path, source_file, output_file]
        subprocess.run(cmd)

        print(f"Processed: {source_file} -> {output_file}")
