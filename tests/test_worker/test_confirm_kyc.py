import pytest
import allure

from data.url import Url
from data.users import TEST_CONFIRM_KYC


@pytest.mark.smoke
@allure.feature("KYC")
@allure.title("Sign by worker and complete KYC")
@allure.description("Success auth by worker and complete KYC")
def test_confirm_kyc(main_page, onboarding_page, clean_db_after_session):

    clean_db_after_session(TEST_CONFIRM_KYC.email)

    main_page.open_main_page()

    main_page.login(email=TEST_CONFIRM_KYC)

    main_page.check_current_page(Url.ONBOARDING_PAGE)

    onboarding_page.click(onboarding_page.button_agree_terms)

    onboarding_page.add_data_onboarding()

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.check_element_visible(main_page.worker_pass_kyc_text)

    main_page.approve_kyc(email=TEST_CONFIRM_KYC.email)

    main_page.refresh_page()

    main_page.check_element_not_visible(main_page.worker_pass_kyc_text)

    main_page.check_current_page(Url.MAIN_PAGE)
