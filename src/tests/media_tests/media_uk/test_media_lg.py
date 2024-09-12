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
def test_media_lg_mm_mv_vm(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LG (LEGOLAND Deutschland)
    # Attraction park is mm = Maximus
    # lv = Maximus Digital
    # The result in this test needs to be: 1 Video for MV, and 1 video for VM
    # In conclusion when looking in GuestApp every digital package have 3 item (including main photo)
    # It's a train of two train carts (two couple of photos to upload)
    ###### End of Explanation ######

    try:
        function_name = test_media_lg_mm_mv_vm.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        lg, mm, mv, vm = substrings  # Unpack the substrings into separate variables

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
                                                                                    'mv')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'mv'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("Delete old Media", "\n# STEP 1.0 - Delete old Media #")

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

            print("\nget media from mv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=mv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\n get media from vm:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=vm,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))
        # No video in this test
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
                                                                             domain=lg,
                                                                             attraction_code=mm,
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
                                                                       domain=lg)
            print(user_id)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=lg,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("STEP 5 - Verification in Angela", "Verification in Angela")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "lg"))

            web_object.go_to_customer_media()

            video_attraction_name_mv = api_helper_media.api_get_attraction_name_in_current_park(site_code=lg,
                                                                                       attraction_code=mv)
            print_log("video attraction name mv", "video_attraction_name_mv is: " + str(video_attraction_name_mv))
            web_object.select_attraction(video_attraction_name_mv)

            result_video_creation_mv = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_mv, media_number_expected=1)
            print_log(f"result video creation mv {result_video_creation_mv}", str(result_video_creation_mv))

            video_attraction_name_vm = api_helper_media.api_get_attraction_name_in_current_park(site_code=lg,
                                                                          attraction_code=vm)

            print_log("video attraction name vm", "video_attraction_name_vm is: " + str(video_attraction_name_vm))
            web_object.select_attraction(video_attraction_name_vm)

            allure.attach(driver.get_screenshot_as_png(), name="test_lg_mm_mv_vm",
                          attachment_type=AttachmentType.PNG)

            result_video_creation_vm = web_object.verify_number_of_created_videos_are_correct(video_attraction_name_vm, media_number_expected=1)
            print_log(f"result video creation vm {result_video_creation_vm}", str(result_video_creation_vm))

            final_result_all_media = web_object.verification_result(result_video_creation_mv, result_video_creation_vm)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_lg_mm_mv_vm",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_lg_mm_mv_vm",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(1))
def test_media_lg_nj_nv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LG (Legoland Deutschland)
    # Attraction park is nj = Ninjago
    # nv = Ninjago Digital
    # The result in this test needs to be: 1 dynamic overlay
    ###### End of Explanation ######

    try:
        function_name = test_media_lg_nj_nv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        lg, nj, nv = substrings  # Unpack the substrings into separate variables

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
                                                                            'LG-NV')),
                                    photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                        AttractionParameters.get_folder_path(
                                                                            'LG-NV'))
                                    )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('LG-NV'))
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

            print("\nget media from tv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=nv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from tt:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=nj,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.LG_NV_ATTRACTION_NAMES.value)

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
                                                                             domain=lg,
                                                                             attraction_code=nj,
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
                                                                       domain=lg)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=lg,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("\nSTEP 5 - Verification in Angela", "Verification in Angela")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "lg"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="lg",
                attraction_code=nv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_lg_nj_nv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_lg_nj_nv",
                      attachment_type=AttachmentType.PNG)

        assert False


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(1))
def test_media_lg_fd_dv(i, driver, application_parameters):
    print_log("Current run in loading test", f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = LG LEGOLAND Deutschland
    # Attraction park is fd = Fire Dragon
    # dv = Fire Dragon Digital
    # The result in this test needs to be: 1 dynamic overlay
    ###### End of Explanation ######

    try:
        function_name = test_media_lg_fd_dv.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        lg, fd, dv = substrings  # Unpack the substrings into separate variables

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
                                                                                    'LG-DV')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'LG-DV'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("STEP 1.0 - Delete old Media", "Delete old Media")

            media_ids_list_for_deletion = []

            uuid_list = connector_helper_object.get_origin_uuids(
                Connector.get_connector_main_path() + AttractionParameters.get_folder_path('LG-DV'))
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

            print("\nget media from tv:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=dv,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            print("\nget media from tt:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=lg,
                                                      attraction_code=fd,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.LG_DV_ATTRACTION_NAMES.value)

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
                                                                             domain=lg,
                                                                             attraction_code=fd,
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
                                                                       domain=lg)

            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=lg,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            print_log("\nSTEP 5 - Verification in Angela", "Verification in Angela")
            # It's just overlay
            time.sleep(120)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_search_customer()

            web_object.search_guest_in_angela_by_user_id(user_id, get_park_full_name(
                "lg"))

            web_object.go_to_customer_media()

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="lg",
                attraction_code=dv)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=1)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=1)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_lg_fd_dv",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_lg_fd_dv",
                      attachment_type=AttachmentType.PNG)

        assert False
