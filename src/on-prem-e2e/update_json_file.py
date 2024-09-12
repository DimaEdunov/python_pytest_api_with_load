import os
import json
import glob


def update_json_file(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    print("before in if 'sk' contains 'portrait' or 'square'")
    # Check if 'configurationId' contains 'portrait' or 'square'
    if 'configurationId' in data and ('portrait' in data['configurationId'] or 'square' in data['configurationId'] or 'sqr' in data['configurationId'] or 'prt' in data['configurationId']):
        print("in if 'sk' contains 'portrait' or 'square'")
        # Add the 'subscribers' field to 'outputs'
        if 'outputs' in data['edl']:
            if 'subscribers' not in data['edl']['outputs']:
                data['edl']['outputs']['subscribers'] = ["mediaProducer"]

    # Check if "print" is in the file path
    if "print" in file_path:
        print("in if 'print' in file_path")
        # Add "nextGenDisplay" to data['edl']['outputs']['subscribers']
        if 'outputs' in data['edl']:
            if 'subscribers' in data['edl']['outputs']:
                if "nextGenDisplay" not in data['edl']['outputs']['subscribers']:
                    data['edl']['outputs']['subscribers'].append("nextGenDisplay")
            else:
                data['edl']['outputs']['subscribers'] = ["mediaProducer", "nextGenDisplay"]

        # Update 'sk' and 'configurationId'
        if 'sk' in data:
            sk_parts = data['sk'].rsplit('_', 1)
            print(f'sk_parts: {sk_parts}')
            print(f'sk_parts[-1]-1: {sk_parts[-1]}')
            sk_parts[-1] = 'print'
            print(f'sk_parts[-1]-2: {sk_parts[-1]}')
            data['sk'] = '_'.join(sk_parts)
            print(f'data["sk"]: {data['sk']}')
        else:
            pass

        if 'configurationId' in data:
            config_parts = data['configurationId'].split('_')
            config_parts[-1] = 'print'
            data['configurationId'] = '_'.join(config_parts)
            print(f'data["configurationId"]: {data['configurationId']}')

    # Check if 'configurationId' contains 'video'
    if 'configurationId' in data and 'video' in data['configurationId']:
        print("in if 'configurationId' contains 'video'")
        # Add the 'subscribers' field to 'outputs'
        if 'outputs' in data['edl']:
            if 'subscribers' not in data['edl']['outputs']:
                data['edl']['outputs']['subscribers'] = ["mediaProducer"]

            # Add the specific structure for 'video'
            video_structure = {
                "type": "short",
                "filename": "${outputs.main.name}_short.mp4",
                "scenes": [1, 2, 3],
                "storage": "local",
                "localPath": "${outputs.short.localpath}",
                "subscriber": "nextGenDisplay",
                "overlays": []
            }
            if 'subProducts' in data['edl']['outputs']:
                exists = False
                for product in data['edl']['outputs']['subProducts']:
                    if product == video_structure:
                        exists = True
                        break
                if not exists:
                    data['edl']['outputs']['subProducts'].append(video_structure)

    # Extract the new file name from 'sk' value
    if 'sk' in data:
        sk_value = data['sk']
        new_file_name = sk_value.split('#')[-1] + '.json'
        print(f'new_file_name: {new_file_name}')
    elif 'configurationId' in data:
        configuration_id_value = data['configurationId']
        new_file_name = configuration_id_value + '.json'

    # Save the updated JSON content to a new file with the new name
    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
    print(f'new_file_path: {new_file_path}')

    if not os.path.exists(new_file_path):
        print("in if os.path.exists(new_file_path)")
        with open(new_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f'Created new file: {new_file_path}')
        # Remove the original file after successfully creating the new file
        print(f'Removing original file: {file_path}')
        os.remove(file_path)
    elif "print" in file_path:
        print("Creating or overwriting file as 'print' is in file_path or file doesn't exist.")
        with open(new_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f'Created new file: {new_file_path}')
    else:
        print(f'New file {new_file_path} already exists. Not creating the file or removing the original.')


def process_directory(dir_path):
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(dir_path, '*.json'))
    print(f'Found {len(json_files)} JSON files.')

    # Update each JSON file
    for json_file in json_files:
        print(f'Processing file: {json_file}')
        update_json_file(json_file)


# Specify the path to your JSON file
directory_path = 'C:\\connector\\test_update_json_file'

# Call the function to process the directory
process_directory(directory_path)
