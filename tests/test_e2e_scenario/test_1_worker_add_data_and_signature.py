import time

import pytest
import allure

from data.url import Url
from data.users import TEST_WORKER


@pytest.mark.smoke
@allure.feature("Sign by worker^")
@allure.title("Create contract")
@allure.description("Success auth and create new contract")
def test_kyc_worker(main_page, onboarding_page):

    main_page.open_main_page()

    main_page.login(email=TEST_WORKER)

    main_page.check_current_page(Url.ONBOARDING_PAGE)

    onboarding_page.click(onboarding_page.button_agree_terms)

    onboarding_page.add_data_onboarding()

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.approve_kyc(email=TEST_WORKER.email)

    main_page.refresh_page()

    main_page.click_fill_address_button()

    onboarding_page.fill_address_info()

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.refresh_page()

    onboarding_page.click(onboarding_page.button_create_withdrawal)

    onboarding_page.click(onboarding_page.button_sepa_withdrawal)

    onboarding_page.click(onboarding_page.button_add_account_withdrawal)

    onboarding_page.fill_withdrawal_data()

    onboarding_page.check_current_page(Url.WITHDRAWAL)

    onboarding_page.check_element_visible(onboarding_page.test_withdrawal_account)

    time.sleep(5)
