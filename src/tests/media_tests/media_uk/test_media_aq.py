import time
import allure
import pytest
from allure_commons.types import AttachmentType

from src.flow_constructors.allure_log import print_log
from src.flow_constructors.angela_page import AngelaPage
from src.flow_constructors.domains import get_park_full_name
from src.flow_constructors.parameters_guests import GuestParameters
from src.flow_constructors.attractions_parameters import AttractionParameters
from src.flow_constructors import api_helper_media, time_calculation
from src.flow_constructors.connector_helper import Connector


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(20))
def test_media_aq_zv_jj(i, driver, application_parameters):
    print(f"\nCurrent run is: {i+1}")
    ###### Explanation ######
    # Domain = TP
    # Attraction park is st = Stealth
    # Attraction video parks are:
    # 1. SV = Stealth ScreamLoadTest Video
    # 2. VS = Stealth ScreamLoadTest Video
    # The result in this test needs to be: 1 Video for SV, and 1 video for VS
    # In conclusion when looking in GuestApp every digital package have 3 times (including main photo)
    # AQ uses keyframe and sync time
    ###### End of Explanation ######

    try:
        function_name = test_media_aq_zv_jj.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        aq, zv, jj = substrings  # Unpack the substrings into separate variables

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
                                                                                    'aq')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'aq'))
                                            )

        print_log("STEP 1.0 - Delete old Media", "Delete old Media")

        media_ids_list_for_deletion = []

        uuid_list = connector_helper_object.get_origin_uuids(
            Connector.get_connector_main_path() + AttractionParameters.get_folder_path('st'))
        for uuid in uuid_list:
            api_helper_media.api_get_media_id_by_uuid(application_parameters['environment'], uuid=uuid,
                                                      list_of_media_ids=media_ids_list_for_deletion)

        # delete old media from the last "time_buffer_in_minutes" value
        api_helper_media.api_delete_media_request(application_parameters['environment'], media_ids_list_for_deletion)

        print("\n# STEP 1.1 - Delete video without originUUID #")
        media_ids_video_list_for_deletion = []

        # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
        time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
            time_buffer_in_minutes=120)

        print("\nget media from sv:")
        api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                  domain=tp,
                                                  attraction_code=sv,
                                                  epoch_from_time=time_values_for_get_media['from'],
                                                  epoch_to_time=time_values_for_get_media['to'],
                                                  list_of_media_ids=media_ids_video_list_for_deletion)

        print("\nget media from vs:")
        api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                  domain=tp,
                                                  attraction_code=vs,
                                                  epoch_from_time=time_values_for_get_media['from'],
                                                  epoch_to_time=time_values_for_get_media['to'],
                                                  list_of_media_ids=media_ids_video_list_for_deletion)

        api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                  media_ids_video_list_for_deletion)

        connector_helper_object.video_drag_and_drop_and_upload()

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=20)

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_aq_zv_jj",
                      attachment_type=AttachmentType.PNG)

        assert False
