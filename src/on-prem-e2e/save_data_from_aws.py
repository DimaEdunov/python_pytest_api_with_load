import os
import random
import time
import boto3
import json
import argparse
from boto3.dynamodb.conditions import Key
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from decimal import Decimal


def decimal_to_int_or_float(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, list):
        return [decimal_to_int_or_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_int_or_float(value) for key, value in obj.items()}
    else:
        return obj


def query_dynamodb(table_name, pk_value, sk_contains_value, json_file_dir, region_name):
    try:
        # Initialize DynamoDB client using a specific profile
        print("Initializing session")
        session = boto3.Session(profile_name='default', region_name=region_name)
        print(f'Session initialized: {session}')
        dynamodb = session.resource('dynamodb')

        # Reference to the DynamoDB table
        table = dynamodb.Table(table_name)
        print(f'table_name: {table_name}')
        print(f'table: {table}')

        # Perform the query
        response = table.query(
            KeyConditionExpression=Key('pk').eq(pk_value) & Key('sk').begins_with(sk_contains_value)
        )

        # Check if items were returned
        if 'Items' in response:
            items = response['Items']
            print(f"Found {len(items)} items")

            # Delay for demonstration purposes
            time.sleep(5)

            # Process each item and save it to a separate JSON file
            for i, item in enumerate(items):
                item_data = decimal_to_int_or_float(item)

                # Initial file path
                file_path = f"{json_file_dir}/item_{i + 1}.json"

                # Check if the file already exists
                while os.path.exists(file_path):
                    # If it does, generate a random number and append it to the filename
                    random_number = random.randint(1000, 9999)
                    file_path = f"{json_file_dir}/item_{random_number}.json"

                with open(file_path, 'w') as json_file:
                    json.dump(item_data, json_file, indent=4)
                print(f"Data saved to {file_path}")
        else:
            print("No items found with the specified criteria")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS configuration.")
    except PartialCredentialsError:
        print("Incomplete credentials provided. Please check your AWS configuration.")
    except ClientError as e:
        print(f"Client error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query DynamoDB and save items to JSON files.')
    parser.add_argument('--pk_value', type=str, required=True, help='The partition key value to query for')
    parser.add_argument('--table_name', type=str, default='media_producer-us-configuration',
                        help='The name of the DynamoDB table')
    parser.add_argument('--region_name', type=str, default='us-west-2', help='The AWS region name')
    args = parser.parse_args()

    sk_contains_value = 'service#mediaEditor'
    json_file_dir = 'C:\\connector\\test_update_json_file'

    query_dynamodb(args.table_name, args.pk_value, sk_contains_value, json_file_dir, args.region_name)
