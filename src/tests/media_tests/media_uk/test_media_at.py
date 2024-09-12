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
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(1))
def test_media_at_sm_sv_vs(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = at (Alton Towers Resort)
    # Attraction park is sm = Smiler
    # sv = Smiler Digital Left
    # vs = Smiler Digital Right
    # The result in this test needs to be: 1 Video for SV, and 1 video for VS
    # In conclusion when looking in GuestApp every digital package have 3 item (including main photo)
    # There are 7 carts in train
    ###### End of Explanation ######

    try:
        function_name = test_media_at_sm_sv_vs.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        at, sm, sv, vs = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AT-SV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AT-SV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AT-SV'))
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

            print("\nget media from sv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=sv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\n get media from vs:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=vs,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AT_SV_ATTRACTION_NAMES.value)

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
                                                                             domain=at,
                                                                             attraction_code=sm,
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
                                                                       domain=at)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=at,
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
                "at"))

            web_object.go_to_customer_media()

            video_attraction_name_sv = api_helper_media.api_get_attraction_name_in_current_park(site_code=at,
                                                                                       attraction_code=sv)
            print_log("video attraction name sv:" + str(video_attraction_name_sv), " ")
            web_object.select_attraction(video_attraction_name_sv)

            result_video_creation_sv = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_sv, media_number_expected=1)
            print_log(f"result video creation sv: {result_video_creation_sv}", " ")

            video_attraction_name_vs = api_helper_media.api_get_attraction_name_in_current_park(site_code=at,
                                                                          attraction_code=vs)

            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_sm_sv_vs",
                          attachment_type=AttachmentType.PNG)

            print_log("video attraction name vs:" + str(video_attraction_name_vs), " ")

            web_object.select_attraction(video_attraction_name_vs)

            result_video_creation_vs = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_vs, media_number_expected=1)
            print_log(f"result of video creation vs {result_video_creation_vs}", str(result_video_creation_vs))

            final_result_all_media = web_object.verification_result(result_video_creation_sv, result_video_creation_vs)

            print_log(f"final result all media in domain 'Alton Towers Resort': {final_result_all_media}", " ")

            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_sm_sv_vs",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_at_sm_sv_vs",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=2)
@pytest.mark.parametrize("i", range(1))
def test_media_at_wm_wv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = at (Alton Towers Resort)
    # Attraction park is wm = Wickerman
    # wv = Wickerman Digital
    # The result in this test needs to be: 1 dynamic overlay
    ###### End of Explanation ######

    try:
        function_name = test_media_at_wm_wv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        at, wm, wv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AT-WV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AT-WV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AT-WV'))
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

            print("\nget media from wv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=wv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AT_WV_ATTRACTION_NAMES.value)

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
                                                                             domain=at,
                                                                             attraction_code=wm,
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
                                                                       domain=at)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=at,
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
                "at"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="at",
                attraction_code=wv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))
            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_wm_wv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_at_wm_wv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=3)
@pytest.mark.parametrize("i", range(1))
def test_media_at_hh_cv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = at (Alton Towers Resort)
    # Attraction park is hh = Curse of Alton Manor
    # cv = Curse of Alton Manor Digital
    # The result in this test needs to be: 1 dynamic overlay
    ###### End of Explanation ######

    try:
        function_name = test_media_at_hh_cv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        at, hh, cv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AT-CV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AT-CV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AT-CV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            if application_parameters['environment'] not in ["us", "uk", "ap"]:
                # delete old media from the last "time_buffer_in_minutes" value
                api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print_log("Delete media in cv attraction, no UUID related", "\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from cv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=cv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AT_CV_ATTRACTION_NAMES.value)

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
                                                                             domain=at,
                                                                             attraction_code=hh,
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
                                                                       domain=at)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=at,
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
                at))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="at",
                attraction_code=cv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))
            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_hh_cv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_at_hh_cv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=4)
@pytest.mark.parametrize("i", range(1))
def test_media_at_ne_nv_left(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = at (Alton Towers Resort)
    # Attraction park is ne = nemesis
    # nv = nemesis Digital
    # The result in this test needs to be: 1 video
    ###### End of Explanation ######

    try:
        function_name = test_media_at_ne_nv_left.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        at, ne, nv, left = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AT-NV-left')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AT-NV-left'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AT-NV-left'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            if application_parameters['environment'] not in ["us", "uk", "ap"]:
                # delete old media from the last "time_buffer_in_minutes" value
                api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print_log("Delete media in cv attraction, no UUID related", "\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from cv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=nv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AT_NV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=at,
                                                                             attraction_code=ne,
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
                                                                       domain=at)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=at,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela domain: 'Alton Towers Resort'", " ")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                at))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="at",
                attraction_code=nv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))
            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_ne_nv_left",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_at_ne_nv_left",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=5)
@pytest.mark.parametrize("i", range(1))
def test_media_at_ne_nv_right(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = at (Alton Towers Resort)
    # Attraction park is ne = nemesis
    # nv = nemesis Digital
    # The result in this test needs to be: 1 video
    ###### End of Explanation ######

    try:
        function_name = test_media_at_ne_nv_right.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        at, ne, nv, right = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AT-NV-right')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AT-NV-right'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "\nDelete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AT-NV-right'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            if application_parameters['environment'] not in ["us", "uk", "ap"]:
                # delete old media from the last "time_buffer_in_minutes" value
                api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print_log("Delete media in cv attraction, no UUID related", "\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\nget media from cv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=at,
                                                      attraction_code=nv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", " ")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AT_NV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=at,
                                                                             attraction_code=ne,
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
                                                                       domain=at)
            print_log("Guest user id: " + user_id, " ")

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=at,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela domain: 'Alton Towers Resort'", " ")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                at))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="at",
                attraction_code=nv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))
            allure.attach(driver.get_screenshot_as_png(), name="test_media_at_ne_nv_right",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_at_ne_nv_right",
                      attachment_type=AttachmentType.PNG)

        assert False