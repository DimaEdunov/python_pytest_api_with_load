import time
import allure
import pytest
from allure_commons.types import AttachmentType
from src.flow_constructors.allure_log import print_log
from src.flow_constructors.angela_page import AngelaPage
from src.flow_constructors.domains import get_park_full_name, get_uuid_status
from src.flow_constructors.parameters_guests import GuestParameters
from src.flow_constructors.attractions_parameters import AttractionParameters
from src.flow_constructors import api_helper_media, time_calculation
from src.flow_constructors.connector_helper import Connector


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(1))
def test_media_ch_ju_jv_vj(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = ch (Chessington World of Adventures)
    # Attraction park is ju = Mandrill Mayhem
    # jv = Mandrill Mayhem Video Left
    # The result in this test needs to be: 1 Video for JV, and 1 video for VJ
    # In conclusion when looking in GuestApp every digital package have 3 item (including main photo)
    # There are 7 carts in train
    ###### End of Explanation ######

    try:
        function_name = test_media_ch_ju_jv_vj.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        ch, ju, jv, vj = substrings  # Unpack the substrings into separate variables

        connector_helper_object = Connector(application_parameters=application_parameters,
                                            photo_upload_path=None,
                                            video_upload_path=None,
                                            photo_source_path=None,
                                            video_source_path=None,
                                            connector_main_path=Connector.get_connector_main_path(),
                                            uploads_path=Connector.get_uploads_path(
                                                Connector.get_connector_main_path()),
                                            video_path=Connector.get_video_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'ju')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'ju'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('ju'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            if application_parameters['environment'] not in ["us", "uk", "ap"]:
                # delete old media from the last "time_buffer_in_minutes" value
                api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print_log("Delete media in nj attraction, no UUID related", "\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from jv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=ch,
                                                      attraction_code=jv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\n get media from vj:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=ch,
                                                      attraction_code=vj,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.JU_ATTRACTION_NAMES.value)

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", " ")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=ch,
                                                                             attraction_code=ju,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print_log("Media IDs - Full list" + str(list_of_media_ids), " ")

            print_log("STEP 4 - Media Association", " ")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=ch)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=ch,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela domain: 'Chessington World of Adventures'", " ")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "ch"))

            web_object.go_to_customer_media()

            video_attraction_name_jv = api_helper_media.api_get_attraction_name_in_current_park(site_code=ch,
                                                                                       attraction_code=jv)
            print_log("video attraction name jv:" + str(video_attraction_name_jv), " ")
            web_object.select_attraction(video_attraction_name_jv)

            result_video_creation_jv = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_jv, media_number_expected=1)
            print_log(f"result video creation jv: {result_video_creation_jv}", " ")

            video_attraction_name_vj = api_helper_media.api_get_attraction_name_in_current_park(site_code=ch,
                                                                          attraction_code=vj)

            allure.attach(driver.get_screenshot_as_png(), name="test_media_ch_ju_jv_vj",
                          attachment_type=AttachmentType.PNG)

            print_log("video attraction name vj:" + str(video_attraction_name_vj), " ")

            web_object.select_attraction(video_attraction_name_vj)

            result_video_creation_vj = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_vj, media_number_expected=1)
            print_log(f"result of video creation vj {result_video_creation_vj}", str(result_video_creation_vj))

            final_result_all_media = web_object.verification_result(result_video_creation_jv, result_video_creation_vj)

            print_log(f"final result all media in domain 'Chessington World of Adventures': {final_result_all_media}", " ")

            allure.attach(driver.get_screenshot_as_png(), name="test_media_ch_ju_jv_vj",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_ch_ju_jv_vj",
                      attachment_type=AttachmentType.PNG)

        assert False