import os
import requests
import argparse

mapping_json_name_to_correct_path = {"kingda_ka": "aj_kv",
                                     "full_throttle": "av_fv"}

url = f'https://uk.picasso-api.picsolve-sandbox.com/config/domain/av/AVFT1_PRE'
headers = {'x-api-key': os.environ.get('domain_host_config_key_on_prem'),
           'Content-Type': 'application/json'}

# The correct host is: ATMT1_DISPLAY \ ATMT1_MEDIA
# Need to change the site_code + attraction_code accordingly
def get_domain_host_api(domain, host):
    url = f'https://uk.picasso-api.picsolve.com/config/domain/{domain}/{host}'
    print(f'url: {url}')
    response = requests.get(url, headers=headers)
    data = response.json()
    if "mediaOnPremSettings" in data['watchedFolders'][0]:
        print(f'data: {data['watchedFolders'][0]['mediaOnPremSettings']}')
    else:
        print("No mediaOnPremSettings in response")


get_domain_host_api('av', 'AVFT1_PRE')

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Query DynamoDB and save items to JSON files.')
#     parser.add_argument('--domain', type=str, required=True, help='domain')
#     parser.add_argument('--host', type=str, help='The name of host in table config_Domain_Hosts')
#     args = parser.parse_args()
#
#     get_domain_host_api(args.domain, args.host)
