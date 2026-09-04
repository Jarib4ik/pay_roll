import pytest
import allure

from data.url import Url
from data.users import TEST_ONBOARDING


@pytest.mark.smoke
@allure.feature("Onboarding")
@allure.title("Sign by worker and complete onboarding")
@allure.description("Success auth by worker and complete onboarding")
def test_onboarding(main_page, onboarding_page, clean_db_after_session):

    clean_db_after_session(TEST_ONBOARDING.email)

    main_page.open_main_page()

    main_page.login(email=TEST_ONBOARDING)

    main_page.check_current_page(Url.ONBOARDING_PAGE)

    onboarding_page.click(onboarding_page.button_agree_terms)

    onboarding_page.add_data_onboarding()

    main_page.check_current_page(Url.MAIN_PAGE)
