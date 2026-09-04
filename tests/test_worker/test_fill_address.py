import time

import pytest
import allure

from data.url import Url
from data.users import TEST_FILL_ADDRESS


@pytest.mark.smoke
@allure.feature("Fill address")
@allure.title("Sign by worker and fil address")
@allure.description("Success auth and fill address")
def test_kyc_worker(main_page, onboarding_page, clean_db_after_session):

    clean_db_after_session(TEST_FILL_ADDRESS.email)

    main_page.open_main_page()

    main_page.login(email=TEST_FILL_ADDRESS)

    main_page.check_current_page(Url.ONBOARDING_PAGE)

    onboarding_page.click(onboarding_page.button_agree_terms)

    onboarding_page.add_data_onboarding()

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.check_element_visible(main_page.worker_pass_kyc_text)

    main_page.approve_kyc(email=TEST_FILL_ADDRESS.email)

    main_page.refresh_page()

    main_page.check_element_not_visible(main_page.worker_pass_kyc_text)

    main_page.check_element_visible(main_page.worker_fill_address_text)

    main_page.click_fill_address_button()

    onboarding_page.fill_address_info()

    main_page.check_element_not_visible(main_page.worker_fill_address_text)

    main_page.check_current_page(Url.MAIN_PAGE)
