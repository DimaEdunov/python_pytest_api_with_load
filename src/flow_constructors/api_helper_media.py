import json
import time
import requests


# Method will return media_id's by: Park, Attraction, Epoch
# Sleep time needs to be adjusted according to upload time via connector
from src.flow_constructors.allure_log import print_log


def api_get_media_id_by_date(environment, domain, attraction_code, epoch_from_time, epoch_to_time, list_of_media_ids):
    # GET media : api/v5/media, filtered by 'from' and 'to' time, based on file CreateTime - TimeStamp
    print("attraction_code in get media: " + attraction_code)
    end_point = f'https://api-{environment}.pomvom.com/api/v5/media?domain={domain}&attractionCode={attraction_code.upper()}&fromTime={epoch_from_time * 1000}&toTime={epoch_to_time * 1000} '
    print("Send GET to : " + str(end_point))

    get_media_id = requests.get(end_point,
                                verify=False,
                                headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa", "x-client-id": "rnd"},
                                )

    response = json.loads(get_media_id.content)
    print("GET Response : " + str(response) + "\n")

    # Parsing response, extracting mediaIds', adding them into a list

    # media_id_counter

    cell_end_index = len(list_of_media_ids)

    media_id_counter = 0
    cell_start_index = cell_end_index
    try:
        for index in range(len(response["media"])):
            print("media id found '%s', createTime: %s - #%s" % (
                response["media"][index]["mediaId"], response["media"][index]["createTime"], index + 1))
            list_of_media_ids.append(response["media"][index]["mediaId"])

            media_id_counter += 1
            cell_end_index += 1

        print("\n")

        # data
        print("media_id counter - total : " + (str(len(list_of_media_ids))))
        print("media_id counter - this bulk : " + (str(media_id_counter)))
        print("Cell start index - " + str(cell_start_index))
        print("Cell end index - " + str(cell_end_index))

        media_id_counter = 0

        return {"start_index": cell_start_index,
                "end_index": cell_end_index,
                "media_ids_this_bulk": media_id_counter,
                "total amount of media_ids": len(list_of_media_ids)}

    except KeyError:
        print_log("No photos found in this cycle", "No photos found in this cycle")


def api_post_associate_media_to_user_id(environment, domain, user_id, media_ids):
    end_point = f'https://api-{environment}.pomvom.com/api/v5/media/accounts/{user_id}'
    print("end_point associate_media_to_user: " + end_point)

    data = {"domain": domain,
            "mediaIds": media_ids}

    associate_media_to_guest = requests.post(end_point,
                                             headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                                      "x-client-id": "rnd",
                                                      "Content-Type": "application/json"},
                                             data=json.dumps(data),
                                             verify=False)

    print(associate_media_to_guest.status_code)
    response = json.loads(associate_media_to_guest.content)

    print(response)

    print_log(f"Association to user: {user_id} to media ID: {media_ids[0]}", "user_id account %s was associated with media_id: %s" % (user_id, media_ids[0]))


def api_delete_media_request(environment, media_list):
    # there is only 200 for response, even if there is no media
    # Delete the media from DB
    end_point = f'https://api-{environment}.pomvom.com/api/v4/media/'

    data = {"mediaIds": media_list}

    delete_media_request = requests.delete(end_point,
                                           headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                                    "x-client-id": "rnd",
                                                    "Content-Type": "application/json"},
                                           data=json.dumps(data),
                                           verify=False)

    response = delete_media_request.status_code
    print("Delete media response: " + str(response))
    print("Media was deleted")


def api_get_userid_by_phone_request(environment, phone_with_country_code, domain):
    end_point = f'https://api-{environment}.pomvom.com/api/v2/users/sign-in/info?phone=%2B{phone_with_country_code}&domain={domain}'
    print(end_point)

    get_guest_by_phone = requests.get(end_point,
                                      verify=False,
                                      headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                               "x-client-id": "rnd"},
                                      )
    response = json.loads(get_guest_by_phone.content)
    print("print response is : " + str(response))
    if "Account does not exist" in response:
        print("*** Account does not exist ***")
        assert False
    else:
        user_id = response['userId']
        return user_id


def api_get_userid_by_email_request(environment, email, domain):
    end_point = f'https://api-{environment}.pomvom.com/api/v2/users/?email={email}&domain={domain}'
    print(end_point)

    get_guest_by_email = requests.get(end_point,
                                      verify=False,
                                      headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                               "x-client-id": "rnd"},
                                      )
    response = json.loads(get_guest_by_email.content)
    print("print response is : " + str(response))
    user_id = response['users'][0]['userId']
    print("user_id in email get: " + str(user_id))
    return user_id


def api_get_media_id_by_uuid(environment, uuid, list_of_media_ids):
    # GET media filtered by originUUID
    print("\n")
    print("The originUUID is: " + str(uuid))
    end_point = f'https://api-{environment}.pomvom.com/api/v4/media/?originUUID={uuid}'
    print("Send GET to : " + str(end_point))

    get_media_id = requests.get(end_point,
                                verify=False,
                                headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa", "x-client-id": "rnd"},
                                )

    response = json.loads(get_media_id.content)
    print("GET Response : " + str(response) + "\n")

    cell_end_index = len(list_of_media_ids)

    try:
        for media in response["result"]['media']:
            if 'mediaId' in media:
                list_of_media_ids.append(media['mediaId'])
        print("number of media in the current uuid: " + str(len(response["result"]['media'])) + "\n")

        # data
        print("media_id counter - total : " + (str(len(list_of_media_ids))))

        return list_of_media_ids

    except KeyError:
        print("No photos found in this cycle")


def api_get_attraction_name_in_current_park(site_code, attraction_code):
    end_point = f'https://uk.picasso-api.picsolve-sandbox.com/config/site/{site_code.upper()}?info=AllAttractionInfo'

    get_attraction_name_in_current_park = requests.get(end_point,
                                                       verify=False,
                                                       headers={
                                                           "x-api-key": "gxbHGI5F2u6SSd9aoIySuVhWQ142oqF6T1ohdzBb"},
                                                       )
    response = json.loads(get_attraction_name_in_current_park.content)
    print("Attraction name get response : " + str(response))
    for dictionary in response:
        if dictionary['Attraction_Code'] == attraction_code.upper():
            return dictionary['Attraction_Name']


def api_get_attraction_configuration(environment, number_end_point, domain, attraction, service, configuration_id):
    end_point = f'https://{number_end_point}.execute-api.eu-west-2.amazonaws.com/{environment}/grouping/groupingConfiguration?domain={domain}&attraction={attraction}&service={service}&configurationId={configuration_id}'
    print("end_point: " + str(end_point))
    get_attraction_configuration = requests.get(end_point,
                                                verify=False,
                                                headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                                         "x-client-id": "rnd"},
                                                )
    response_content = get_attraction_configuration.content.decode('utf-8')
    response = json.loads(response_content)
    response_dumps = json.dumps(response, indent=4)
    print(f'Fot attraction- {attraction}, the get response is:' + response_dumps)
    return response_dumps


def api_post_configuration(result, environment, number_end_point, service_name, body):
    if result == False:
        end_point = f'https://{number_end_point}.execute-api.eu-west-2.amazonaws.com/{environment}/grouping/{service_name}Configuration'
        print("end_point: " + str(end_point))

        post_configuration = requests.post(end_point,
                                           data=json.dumps(body),
                                           verify=False,
                                           headers={"Content-Type": "application/json"})
        print("json.dumps(body)")
        print(json.dumps(body))
        print(post_configuration.status_code)
        response = json.loads(post_configuration.content)

        print(response)
    else:
        pass


def api_amount_of_excution(environment, domain, origin_uuid):
    end_point = f'https://gateway-{environment}.pomvom.com/api/v1/media-producer/step/duplicateexecutions?domain={domain}&originUUIDs={origin_uuid}'
    print("end_point: " + str(end_point))

    get_group_id_of_execution = requests.get(end_point,
                                      verify=True,
                                      headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                               "x-client-id": "rnd"},
                                      )
    response = json.loads(get_group_id_of_execution.content)
    print("group_id_of_execution: " + str(response))
    if not response:
        print("No duplicates")
    else:
        print("**** There are duplicate executions ****")


