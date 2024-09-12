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
def test_media_llfl_cc_dv(i, driver, application_parameters):
    print(f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = llfl
    # Attraction park is CC = The Dragon
    # Attraction video park is DV = The Dragon Video
    # The result in this test needs to be: every photo have 2 videos (1 long + 1 short video),
    # 2 overlay photos (1 landscape + 1 portrait)
    # In conclusion when looking in Angela every digital package have 5 items (including main photo)
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_cc_dv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, cc, dv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'dv')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'dv'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1 - Delete old Media", "\nDelete old Media")
            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('dv'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" variable
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete old video without originUUID #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from cc:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=cc,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from dv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=dv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        # connector_helper_object.change_image_comments()

        print_log("STEP 2 - Media File Handling", "Media File Handling")

        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.DV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

        # forced Create Time change to current time in timestamp ms format
        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:

            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=cc,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media['from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print_log("Media IDs - Full list", "Media IDs - Full list " + str(list_of_media_ids))

            print_log("#STEP 4 - Media Association#", "\nMedia Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            print_log("phone number of guest", "phone_number " + str(phone_number))
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])
            print_log("STEP 5 - Verification in Angela", "\nVerification in Angela")
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                application_parameters['site_code'],
                attraction_code=dv)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=4)
            print_log(f"result all media creation {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name, media_number_expected=2)
            print_log(f"result video creation {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_cc_dv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_cc_dv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=2)
@pytest.mark.parametrize("i", range(1))
def test_media_llfl_te_tv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = llfl
    # Attraction park is TE = The Great Lego Race
    # Attraction video park is TV = The Great Lego Race - Video
    # The result in this test needs to be: 1 video, 1 overlay
    # media editor and sync time
    # Every photo uploaded needs to have the correct video (not just any video)
    # Matching photo-video in folder: "photos with sync"
    # TV uses keyframe and sync time
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_te_tv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, te, tv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'LF-TV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'LF-TV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('LF-TV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print_log("STEP 1.1 - Delete old video without originUUID", "Delete old video without originUUID")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\n get media from tv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=tv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.TV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=60)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("#STEP 3 - Getting Media Ids#", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=te,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media['from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print_log("Media IDs - Full list", "Media IDs - Full list : " + str(list_of_media_ids))

            print("STEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)
            print_log(f"phone number: {phone_number}", phone_number)
            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Verification in Angela")
            time.sleep(180)
            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                application_parameters['site_code'],
                attraction_code=tv)

            print_log(f"video attraction name tv {video_attraction_name}", video_attraction_name)
            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=2)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)
            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_te_tv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_te_tv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=3)
@pytest.mark.parametrize("i", range(1))
def test_media_llfl_co_cv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = llfl
    # Attraction park is CO = Coastersaurus
    # Attraction video park is CV = Coastersaurus - Digital
    # The result in this test needs to be: every photo have 1 video (long video),
    # 2 overlay photos (1 landscape + 1 portrait)
    # In conclusion when looking in GuestApp every digital package have 4 times (including main photo)
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_co_cv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, co, cv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'cv')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'cv'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('cv'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete old video without originUUID #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from dv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=cv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.CO_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=60)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=co,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media['from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print("Media IDs - Full list : " + str(list_of_media_ids))

            print_log("STEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Verification in Angela")
            time.sleep(180)
            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                application_parameters['site_code'],
                attraction_code=cv)

            print_log(f"video attraction name cv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_co_cv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_co_cv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=4)
@pytest.mark.parametrize("i", range(1))
def test_media_llfl_nj_nv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LF
    # Attraction park is nj = Ninjago - The Ride
    # The result in this test needs to be: 1 dynamic overlay square
    # In conclusion when looking in GuestApp every digital package have 1 item (including main photo)
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_nj_nv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, nj, nv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'nj')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'nj'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('nj'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from nj:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=nj,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from nv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=nv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.NJ_ATTRACTION_NAMES.value)

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=nj,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print_log("Media IDs - Full list:", "Media IDs - Full list: " + str(list_of_media_ids))

            print_log("STEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(site_code="lf",
                                                                                       attraction_code=nv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_nj_nv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_nj_nv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=5)
@pytest.mark.parametrize("i", range(1))
def test_media_llfl_pp_pv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LF
    # Attraction park is pp = Daddy Pigs Roller Coaster
    # pv = Daddy Pigs Roller Coaster Video
    # The result in this test needs to be: 1 dynamic Overlay
    # In conclusion when looking in GuestApp every digital package have 1 item (including main photo)
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_pp_pv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, pp, pv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'pv')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'pv'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('pv'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from pv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=pv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from pp:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=pp,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.PV_ATTRACTION_NAMES.value)

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=pp,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print("Media IDs - Full list : " + str(list_of_media_ids))

            print_log("\nSTEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Verification in Angela")
            # It's just overlay
            time.sleep(60)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="lf",
                attraction_code=pv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_pp_pv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_pp_pv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=6)
@pytest.mark.parametrize("i", range(1))
def test_media_llfl_lk_lv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LF
    # Attraction park is lk = Lost Kingdom Adventure
    # lv = Lost Kingdom Adventure Digital
    # The result in this test needs to be: 1 dynamic overlay
    # In conclusion when looking in GuestApp every digital package have 2 item (including main photo)
    # It's a train of two train carts (two couple of photos to upload)
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_lk_lv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, lk, lv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'lv')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'lv'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('lv'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from lv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=lv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from lk:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=llfl,
                                                      attraction_code=lk,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.LK_ATTRACTION_NAMES.value)

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=llfl,
                                                                             attraction_code=lk,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'from'],
                                                                             epoch_to_time=time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print("Media IDs - Full list : " + str(list_of_media_ids))

            print_log("STEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'], phone_number,
                                                                       domain=llfl)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("\nSTEP 5 - Verification in Angela", "Verification in Angela")
            # It's just overlay
            time.sleep(60)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "llfl"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="lf",
                attraction_code=lv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_lk_lv",
                      attachment_type=AttachmentType.PNG)

        assert False
