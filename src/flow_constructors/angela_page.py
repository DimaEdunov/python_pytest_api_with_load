import os
import time
import allure
from allure_commons.types import AttachmentType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from src.flow_constructors.allure_log import print_log
from src.flow_constructors.domains import get_angela_login_credentials
from src.flow_constructors.web_elements_app import WebElementApp


class AngelaPage(object):

    def __init__(self, driver, application_parameters):
        self.driver = driver
        self.domain = application_parameters["domain"]
        self.environment = application_parameters["environment"]

    @allure.step("verify_all_media_created() | verify all media created")
    def verify_all_media_created(self, media_number_expected):
        time.sleep(2)
        media_in_attraction = self.driver.find_elements(By.XPATH, WebElementApp.ALL_MEDIA_IN_VIDEO_ATTRACTION.value)

        print_log(f"verify all media created, media number expected: {media_number_expected}, real number of "
                  f"media in attraction: {len(media_in_attraction)}", "verify_all_media_created")
        if len(media_in_attraction) == media_number_expected:
            return True
        else:
            return False

    @allure.step("verified_number_of_created_videos_are_correct() | Verified_number_of_created_videos_are_correct")
    def verify_number_of_created_videos_are_correct(self, attraction_name, media_number_expected):
        time.sleep(2)
        media_in_attraction = self.driver.find_elements(By.XPATH, WebElementApp.VIDEO_ICON_IN_VIDEO_THUMBNAIL.value)

        print_log(f"{attraction_name} verify number of created videos are correct, media number expected: {media_number_expected}, real "
                  f"number of videos in attraction: {len(media_in_attraction)}", "verify_number_of_created_videos_are_correct")
        if len(media_in_attraction) == media_number_expected:
            return True
        else:
            return False

    @allure.step("verified_number_of_created_videos_are_correct() | Verified_number_of_created_videos_are_correct")
    def verification_result(self, result_all_media_creation, result_video_creation):
        if result_all_media_creation and result_video_creation == True:
            assert True
            return True
        else:
            print_log("verification result is false", "verification result is false, mining the media wasn't created or was creates wrong")
            assert False

    def angela_url(self):
        url = "https://angela-%s.pomvom.com/" % self.environment
        return url

    @allure.step("MenuPage.angela_login() | Login to angela")
    def angela_login(self):
        time.sleep(3)
        if len(self.driver.find_elements(By.XPATH, '//div[@class="flex justify-center items-center"]')) > 0:
            pass

        elif len(self.driver.find_elements(By.XPATH, "//div[contains(text(),'Welcome')]")) > 0:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '(//button[@type="button"])[2]'))).click()
            time.sleep(2)

            azure_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@value='Azure'])[2]")))
            time.sleep(3)
            azure_button.click()
            print("****xxxx****")
        # login 2nd time
        elif len(self.driver.find_elements(By.XPATH, '(//form//button[@type="submit"])[2]')) > 0:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '(//form//button[@type="submit"])[2]'))).click()
            time.sleep(3)
        else:
            # Full login
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@title="Azure AD ・ Pomvom Microsoft Account"]'))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]'))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]'))).send_keys(
                get_angela_login_credentials('user'))
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).send_keys(
                get_angela_login_credentials('password'))
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//button[@class="button button button--rounded button--login button--secondary button--outline"]'))).click()

            time.sleep(2)
            azure_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@value='Azure'])[2]")))
            time.sleep(3)
            azure_button.click()

    @allure.step("MenuPage.go_to_search_customer() | go to search customer")
    def go_to_search_customer(self):
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, WebElementApp.SEARCH_CUSTOMER_BUTTON.value))).click()
        time.sleep(6)

    @allure.step("SearchCustomerPage.search_guest_in_angela_by_user_id() | search guest in angela by user id")
    def search_guest_in_angela_by_user_id(self, get_user_id, park_name):
        self.search_customer_park_picklist_item(self.driver, park_name)

        time.sleep(6)
        user_id_field = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, WebElementApp.SEARCH_CUSTOMER_USER_ID_OR_PHONE_FIELD.value)))
        user_id_field.click()
        time.sleep(2)
        user_id_field.send_keys(get_user_id)

        time.sleep(2)

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, WebElementApp.SEARCH_CUSTOMER_SEARCH_BUTTON_BY_USER_ID_OR_PHONE.value))).click()

        time.sleep(4)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, WebElementApp.SEARCH_CUSTOMER_USER_FOUND.value))).click()

        time.sleep(2)

    @staticmethod
    def search_customer_park_picklist_item(driver, domain_name):
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, WebElementApp.OPEN_SEARCH_CUSTOMER_PARK_PICKLIST.value))).click()

        select_attraction = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'%s') and contains(@class,'q-item')]" % domain_name)))

        actions = ActionChains(driver)
        actions.move_to_element(select_attraction).perform()
        time.sleep(1)
        select_attraction.click()

    @allure.step("MenuPage.go_to_customer_media() | go to customer media")
    def go_to_customer_media(self):
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, WebElementApp.CUSTOMER_MEDIA_BUTTON.value))).click()
        time.sleep(6)

    @allure.step("CustomerMediaPage.delete_media_from_cloud_via_angela() | delete media from cloud via angela")
    def delete_media_from_angela(self):
        time.sleep(1)
        if len(self.driver.find_elements(By.XPATH, WebElementApp.CUSTOMER_MEDIA_MEDIA_TAB_PHOTOS.value)) > 0:
            media_of_customer = self.driver.find_elements(By.XPATH, WebElementApp.CUSTOMER_MEDIA_MEDIA_TAB_PHOTOS.value)
            number_media_of_customer = len(media_of_customer)

            while number_media_of_customer > 0:
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, WebElementApp.CUSTOMER_MEDIA_MEDIA_TAB_PHOTOS.value))).click()
                time.sleep(1)
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, WebElementApp.CUSTOMER_MEDIA_MEDIA_DETAILS_DELETE_BUTTON.value))).click()
                time.sleep(1)
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, WebElementApp.CUSTOMER_MEDIA_CONFIRM_DELETE_MEDIA_YES_BUTTON.value))).click()
                time.sleep(1)
                number_media_of_customer -= 1

            else:
                print("debug - No media to delete")
                pass
        else:
            print("debug - No media to delete")
            pass

    @allure.step("CustomerMediaPage.select_attraction() | Select_attraction")
    def select_attraction(self, attraction_name):
        time.sleep(5)
        customer_media_attraction_field = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, WebElementApp.CUSTOMER_MEDIA_SELECT_ATTRACTION_PICKLIST.value)))
        customer_media_attraction_field.click()

        self.customer_media_choose_attraction_picklist_item(attraction_name)

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, WebElementApp.CUSTOMER_MEDIA_SEARCH_BUTTON.value))).click()

        time.sleep(2)

    @allure.step("customer_media_choose_attraction_picklist_item() | Customer_media_choose_attraction_picklist_item")
    def customer_media_choose_attraction_picklist_item(self, attraction_name):
        select_attraction = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='%s']" % attraction_name)))
        actions = ActionChains(self.driver)
        actions.move_to_element(select_attraction).perform()
        time.sleep(1)
        select_attraction.click()

    @allure.step("MenuPage.go_to_search_customer() | go to search customer")
    def go_to_search_customer(self):
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, WebElementApp.SEARCH_CUSTOMER_BUTTON.value))).click()
        time.sleep(6)

    @allure.step("CustomerMediaPage.select_park_in_customer_media() | Select park in customer media")
    def select_park_in_customer_media(self, park_name):
        time.sleep(2)
        park_picklist = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, WebElementApp.CUSTOMER_MEDIA_PARK_PICKLIST.value)))

        park_picklist.click()

        time.sleep(1)

        select_park = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'%s') and contains(@class,'q-item')]" % park_name)))
        actions = ActionChains(self.driver)
        actions.move_to_element(select_park).perform()
        time.sleep(1)
        select_park.click()

        # Needs to be deleted after after Adan fix park showing twice
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, WebElementApp.CUSTOMER_MEDIA_SEARCH_BUTTON.value))).click()
