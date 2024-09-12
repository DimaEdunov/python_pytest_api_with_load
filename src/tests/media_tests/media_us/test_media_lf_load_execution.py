import time
import allure
import pytest
from allure_commons.types import AttachmentType

from src.flow_constructors.domains import get_uuid_status
from src.flow_constructors.allure_log import print_log
from src.flow_constructors.parameters_guests import GuestParameters
from src.flow_constructors.attractions_parameters import AttractionParameters
from src.flow_constructors import api_helper_media, time_calculation
from src.flow_constructors.connector_helper import Connector


@pytest.mark.usefixtures("driver", "application_parameters")
@pytest.mark.regression
# @pytest.mark.dev
@pytest.mark.run(order=7)
@pytest.mark.parametrize("i", range(20))
def test_media_llfl_cc_dv_load(i, driver, application_parameters):
    print(f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Load testing
    ###### End of Explanation ######

    try:
        function_name = test_media_llfl_cc_dv_load.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        llfl, cc, dv, load = substrings  # Unpack the substrings into separate variables

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

        print_log("STEP 2 - Media File Handling", "Media File Handling")
        ### There is no return in the renaming_uuid_in_photo_files method ###
        origin_uuid = connector_helper_object.renaming_uuid_in_photo_files(uuid_assignment=get_uuid_status("jpg_pairs"))

        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.DV_ATTRACTION_NAMES.value)

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
            # First association
            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])
            time.sleep(0.5)
            # Second association
            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            phone_number_load_1 = GuestParameters.get_country_code() + GuestParameters.get_phone_guest_loading_1()
            print_log("phone number of guest", "phone_number " + str(phone_number))
            user_id_load_1 = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'],
                                                                       phone_number_load_1,
                                                                       domain=llfl)
            time.sleep(0.5)
            # third association
            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id_load_1,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            time.sleep(5)

            phone_number_load_2 = GuestParameters.get_country_code() + GuestParameters.get_phone_guest_loading_2()
            print_log("phone number of guest", "phone_number " + str(phone_number))
            user_id_load_2 = api_helper_media.api_get_userid_by_phone_request(application_parameters['environment'],
                                                                              phone_number_load_2,
                                                                              domain=llfl)
            # Forth association
            api_helper_media.api_post_associate_media_to_user_id(application_parameters['environment'],
                                                                 domain=llfl,
                                                                 user_id=user_id_load_2,
                                                                 media_ids=[list_of_media_ids[
                                                                                media_id_output_data['start_index']]])

            api_helper_media.api_amount_of_excution(application_parameters['environment'], domain=llfl, origin_uuid=origin_uuid)

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_llfl_cc_dv",
                      attachment_type=AttachmentType.PNG)

        assert False