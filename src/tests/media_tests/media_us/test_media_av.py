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
def test_media_av_ta_tv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is ta = Tatsu
    # tv = Tatsu - Video
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_ta_tv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, ta, tv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-TV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-TV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-TV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from ta:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=ta,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from tv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=tv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_TV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=ta,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=tv)

            print_log(f"video attraction name tv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_ta_tv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_ta_tv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=2)
@pytest.mark.parametrize("i", range(1))
def test_media_av_cb_cv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is cb = Canyon Blaster
    # cv = Canyon Blaster - Video
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_cb_cv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, cb, cv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-CV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-CV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-CV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from cb:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=cb,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from cv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=cv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_CV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=55)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            # Calculate current GMT time, add buffer for : from, to
            time_filter_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_seconds(
                application_parameters['from_to_api_time_buffer_seconds'])

            list_of_media_ids = []

            # GET, mediaId's of the server
            print_log("STEP 3 - Getting Media Ids", "Getting Media Ids")
            media_id_output_data = api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                                             domain=av,
                                                                             attraction_code=cb,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=cv)

            print_log(f"video attraction name cv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_cb_cv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_cb_cv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=3)
@pytest.mark.parametrize("i", range(1))
def test_media_av_wc_wv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is wc = West Coaster Racers
    # wv = West Coaster Racers - Video
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_wc_wv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, wc, wv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-WV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-WV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-WV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from wc:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=wc,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from wv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=wv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_WC_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=wc,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=wv)

            print_log(f"video attraction name wv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_wc_wv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_wc_wv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=4)
@pytest.mark.parametrize("i", range(1))
def test_media_av_xt_xv_left(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is xt = X2
    # xv = X2 - Digital
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_xt_xv_left.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, xt, xv, left = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-XV-left')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-XV-left'))
                                            )

        # if application_parameters['environment'] not in ["us", "uk", "ap"]:
        #     print_log("STEP 1.0 - Delete old Media", "Delete old Media")
        #
        #     media_ids_list_for_deletion = []
        #
        #     uuid_list = connector_helper_object.get_origin_uuids(
        #         Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-XV-left'))
        #     for uuid in uuid_list:
        #         api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
        #                                                   list_of_media_ids=media_ids_list_for_deletion)
        #
        #     # delete old media from the last "time_buffer_in_minutes" value
        #     api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)
        #
        #     print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
        #     media_ids_video_list_for_deletion = []
        #
        #     # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
        #     time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
        #         time_buffer_in_minutes=120)
        #
        #     print("\nget media from xt:")
        #     api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
        #                                               domain=av,
        #                                               attraction_code=xt,
        #                                               epoch_from_time=time_values_for_get_media['from'],
        #                                               epoch_to_time=time_values_for_get_media['to'],
        #                                               list_of_media_ids=media_ids_video_list_for_deletion)
        #
        #     print("\nget media from xv:")
        #     api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
        #                                               domain=av,
        #                                               attraction_code=xv,
        #                                               epoch_from_time=time_values_for_get_media['from'],
        #                                               epoch_to_time=time_values_for_get_media['to'],
        #                                               list_of_media_ids=media_ids_video_list_for_deletion)
        #
        #     api_helper_media.api_delete_media_request(application_parameters['environment'],
        #                                               media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_XV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=xt,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=xv)

            print_log(f"video attraction name xv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_xt_xv_left",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_xt_xv_lest",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=5)
@pytest.mark.parametrize("i", range(1))
def test_media_av_xt_xv_right(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is xt = X2
    # xv = X2 - Digital
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_xt_xv_right.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, xt, xv, right = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-XV-right')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-XV-right'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-XV-right'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from xt:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=xt,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from xv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=xv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_XV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=xt,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=xv)

            print_log(f"video attraction name xv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_xt_xv_right",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_xt_xv_right",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=6)
@pytest.mark.parametrize("i", range(1))
def test_media_av_ft_fv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is ft = Full Throttle
    # fv = Full Throttle - Digital
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_ft_fv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, ft, fv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-FV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-FV'))
                                            )

        # if application_parameters['environment'] not in ["us", "uk", "ap"]:
        #     print_log("STEP 1.0 - Delete old Media", "Delete old Media")
        #
        #     media_ids_list_for_deletion = []
        #
        #     uuid_list = connector_helper_object.get_origin_uuids(
        #         Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-FV'))
        #     for uuid in uuid_list:
        #         api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
        #                                                   list_of_media_ids=media_ids_list_for_deletion)
        #
        #     # delete old media from the last "time_buffer_in_minutes" value
        #     api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)
        #
        #     print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
        #     media_ids_video_list_for_deletion = []
        #
        #     # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
        #     time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
        #         time_buffer_in_minutes=120)
        #
        #     print("\nget media from ft:")
        #     api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
        #                                               domain=av,
        #                                               attraction_code=ft,
        #                                               epoch_from_time=time_values_for_get_media['from'],
        #                                               epoch_to_time=time_values_for_get_media['to'],
        #                                               list_of_media_ids=media_ids_video_list_for_deletion)
        #
        #     print("\nget media from fv:")
        #     api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
        #                                               domain=av,
        #                                               attraction_code=fv,
        #                                               epoch_from_time=time_values_for_get_media['from'],
        #                                               epoch_to_time=time_values_for_get_media['to'],
        #                                               list_of_media_ids=media_ids_video_list_for_deletion)
        #
        #     api_helper_media.api_delete_media_request(application_parameters['environment'],
        #                                               media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_FV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=ft,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=fv)

            print_log(f"video attraction name fv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_ft_fv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_ft_fv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=7)
@pytest.mark.parametrize("i", range(1))
def test_media_av_vi_vv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is vi = Viper
    # vv = Viper - Digital
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_vi_vv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, vi, vv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-VV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-VV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-VV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from vi:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=vi,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from vv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=vv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_VV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=vi,
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
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=vv)

            print_log(f"video attraction name vv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_vi_vv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_vi_vv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=8)
@pytest.mark.parametrize("i", range(1))
def test_media_av_go_gv(i, driver, application_parameters):
    print("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = AV (Six Flags Magic Mountain)
    # Attraction park is go = Goliath
    # gv = Goliath Video
    # The result in this test needs to be: 1 Video,  1 portrait, 1 square
    ###### End of Explanation ######

    try:
        function_name = test_media_av_go_gv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        av, go, gv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'AV-GV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'AV-GV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('AV-GV'))
            for uuid in uuid_list:
                api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                          list_of_media_ids=media_ids_list_for_deletion)

            # delete old media from the last "time_buffer_in_minutes" value
            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_list_for_deletion)

            print("\n# STEP 1.1 - Delete media in nj attraction, no UUID related #")
            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=120)

            print("\nget media from ta:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=go,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from tv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=av,
                                                      attraction_code=gv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        # There is now video to upload
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.AV_GV_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

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
                                                                             domain=av,
                                                                             attraction_code=go,
                                                                             epoch_from_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'from'],
                                                                             epoch_to_time=
                                                                             time_filter_values_for_get_media[
                                                                                 'to'],
                                                                             list_of_media_ids=list_of_media_ids)

            print_log("Media IDs - Full list:", "Media IDs - Full list: " + str(list_of_media_ids))

            print_log("STEP 4 - Media Association", "Media Association")
            phone_number = GuestParameters.get_country_code() + GuestParameters.get_phone_guest()
            user_id = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'],
                                                                       phone_number,
                                                                       domain=av)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=av,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Media Association")
            # It's just overlay
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "av"))

            web_object.go_to_customer_media()

            web_object.go_to_customer_media()

            video_attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code=av,
                attraction_code=gv)

            print_log(f"video attraction name bv {video_attraction_name}", video_attraction_name)

            web_object.select_attraction(video_attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=3)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(video_attraction_name,
                                                                                           media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_av_go_gv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_av_go_gv",
                      attachment_type=AttachmentType.PNG)

        assert False
