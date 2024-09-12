import time
import allure
import pytest
from allure_commons.types import AttachmentType

from src.flow_constructors.allure_log import print_log
from src.flow_constructors.angela_page import AngelaPage
from src.flow_constructors.domains import get_park_full_name
from src.flow_constructors.attractions_parameters import AttractionParameters
from src.flow_constructors import api_helper_media, time_calculation
from src.flow_constructors.connector_helper import Connector


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.run(order=1)
@pytest.mark.parametrize("i", range(1))
def test_media_fu_to(i, driver, application_parameters):
    print(f"\nCurrent run is: {i + 1}")
    ###### Explanation ######
    # Domain = FU (Futuroscope Theme Park)
    # Attraction park is TO = Chasseurs de Tornades
    # The result in this test needs to be: 3 overlays (background remove) for each photo uploaded
    # No need for UUID
    # No association needed
    # There is no configuration from Ayelet (No Background removal from Sharon)
    # The Background removal happens in the IPP for now (Adam)
    ###### End of Explanation ######

    try:
        function_name = test_media_fu_to.__name__  # Get the name of the function
        substrings = function_name.split("_")[2:]  # Select substrings starting from the third one
        fu, to = substrings  # Unpack the substrings into separate variables

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
                                                                                    'FU-TO')),
                                            photo_path=Connector.get_photo_path(Connector.get_connector_main_path(),
                                                                                AttractionParameters.get_folder_path(
                                                                                    'FU-TO'))
                                            )

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print("\n# STEP 1.0 - Delete old Media #")

            media_ids_video_list_for_deletion = []

            # Calculate current GMT time, add buffer for : from= the time that is passed in method, to= current time
            time_values_for_get_media = time_calculation.media_testing_from_to_time_calculation_in_minutes(
                time_buffer_in_minutes=540)

            print("\n get media from to:")
            api_helper_media.api_get_media_id_by_date(application_parameters['environment'],
                                                      domain=fu,
                                                      attraction_code=to,
                                                      epoch_from_time=time_values_for_get_media['from'],
                                                      epoch_to_time=time_values_for_get_media['to'],
                                                      list_of_media_ids=media_ids_video_list_for_deletion)

            api_helper_media.api_delete_media_request(application_parameters['environment'],
                                                      media_ids_video_list_for_deletion)

        print("#STEP 2 - Media File Handling#")
        connector_helper_object.photos_drag_and_drop_and_upload(
            attraction_names=AttractionParameters.FU_TO_ATTRACTION_NAMES.value)

        connector_helper_object.video_drag_and_drop_and_upload()

        connector_helper_object.edit_config_file()

        connector_helper_object.run_connector(time_out=45)

        if application_parameters['environment'] not in ["us", "uk", "ap"]:
            print_log("\nSTEP 5 - Verification in Angela", "Verification in Angela")
            time.sleep(180)

            web_object = AngelaPage(driver, application_parameters)

            driver.get(web_object.angela_url())

            web_object = AngelaPage(driver, application_parameters)

            web_object.angela_login()

            web_object.go_to_customer_media()

            full_park_name = get_park_full_name(
                "fu")

            print("full_park_name: " + str(full_park_name))

            web_object.select_park_in_customer_media(full_park_name)

            attraction_name = api_helper_media.api_get_attraction_name_in_current_park(
                site_code="fu",
                attraction_code=to)
            print_log(f"attraction name: {attraction_name}", attraction_name)

            web_object.select_attraction(attraction_name)

            result_all_media_creation = web_object.verify_all_media_created(media_number_expected=6)
            print_log(f"result all media creation: {result_all_media_creation}", str(result_all_media_creation))

            result_video_creation = web_object.verify_number_of_created_videos_are_correct(attraction_name, media_number_expected=0)
            print_log(f"result video creation: {result_video_creation}", str(result_video_creation))

            final_result_all_media = web_object.verification_result(result_all_media_creation, result_video_creation)

            print_log(f"final result all media: {final_result_all_media}", str(final_result_all_media))

            allure.attach(driver.get_screenshot_as_png(), name="test_media_fu_to",
                          attachment_type=AttachmentType.PNG)

            web_object.go_to_search_customer()

    except:
        allure.attach(driver.get_screenshot_as_png(), name="test_media_fu_to",
                      attachment_type=AttachmentType.PNG)

        assert False
