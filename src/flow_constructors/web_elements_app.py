import enum


class WebElementApp(enum.Enum):
    # Angela - menu page
    CUSTOMER_MEDIA_BUTTON = "//a[contains(@href, '/customer-media')]"
    SEARCH_CUSTOMER_BUTTON = "//a[contains(@href, '/search-customer')]"
    ANGELA_USER_NAME_LOGGED_IN = "//span[@class='q-ml-md text-primary']"
    ANGELA_LOGIN_REFFERANCE_ELEMENT = "//div[contains(text(),'Welcome')]"

    # Angela - customer media page
    CUSTOMER_MEDIA_SELECT_PARK_PICKLIST = "//label[@for='parkSelect']/following-sibling::label"
    CUSTOMER_MEDIA_SELECT_ATTRACTION_PICKLIST = "(//form//label[contains(@class, 'q-select--single q-field--outlined')])[2]"
    CUSTOMER_MEDIA_SEARCH_BUTTON = "//div[@class='self-end q-ml-md']//i[contains(@class, 'text-white notranslate')]"
    CUSTOMER_MEDIA_FIRST_PHOTO = "(//div[@class='column absolute-center full-width full-height'])[1]"
    MEDIA_DETAILS_PREFIX_PLUS_MEDIA_NUMBER = "//span[contains(text(), 'Prefix')]/following-sibling::span"
    MEDIAS_IN_CUSTOMER_MEDIA = "//main//div[@class='relative-position photo-grid__item observable']"
    SELECT_MEDIA_IN_CUSTOMER_MEDIA = "//button[@class='button button--icon photo-menu__button']"
    CUSTOMER_MEDIA_ADD_BUTTON = "//button[contains(text(), 'Add')]"
    CUSTOMER_MEDIA_ADD_PHOTO_BUTTON_IN_MEDIA_DETAILS = "//button[contains(text(), 'Add Photos')]"
    CUSTOMER_MEDIA_MEDIA_TAB_PHOTOS = "//div[@class='full-height col tab-shadow q-scrollarea']//div[@role='img']"
    CUSTOMER_MEDIA_MEDIA_DETAILS_DELETE_BUTTON = "//button[contains(text(), 'Delete')]"
    CUSTOMER_MEDIA_CONFIRM_DELETE_MEDIA_YES_BUTTON = "//span[contains(text(), 'Yes')]"
    CUSTOMER_MEDIA_PARK_PICKLIST = '(//div[@class="q-field__append q-field__marginal row no-wrap items-center q-anchor--skip"])[1]'
    ALL_MEDIA_IN_VIDEO_ATTRACTION = '//div[@class="col-2"]'
    VIDEO_ICON_IN_VIDEO_THUMBNAIL = '//div[@class="photo-menu__video text-body2"]'

    # Angela search customer page
    SEARCH_CUSTOMER_USER_ID_OR_PHONE_FIELD = "(//input[contains(@class,'q-field__native')])[1]"
    SEARCH_CUSTOMER_SEARCH_BUTTON_BY_USER_ID_OR_PHONE = "(//button[contains(@class, 'button--icon')])[1]"
    SEARCH_CUSTOMER_USER_FOUND = "//div[contains(@class, 'q-img__content')]"
    OPEN_SEARCH_CUSTOMER_PARK_PICKLIST = "//div[@id='parkSelect']"

    # Angela customer information page
    CUSTOMER_INFORMATION_PRICE_OF_TICKET = "(//td[@class='text-left item-subtitle'])[7]"

    # navigate between upper tool bar
    TOOL_BAR_NAVIGATION = "//div[@class='q-tab__label']"

