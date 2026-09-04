import pytest
import allure

from data.url import Url
from data.users import TEST_LOGOUT


@pytest.mark.smoke
@allure.feature("Logout")
@allure.title("Sign by worker, complete onboarding and logout")
@allure.description("Success auth by worker, complete onboarding and logout")
def test_logout(main_page, onboarding_page, profile_page, clean_db_after_session):

    clean_db_after_session(TEST_LOGOUT.email)

    main_page.open_main_page()

    main_page.login(email=TEST_LOGOUT)

    main_page.check_current_page(Url.ONBOARDING_PAGE)

    onboarding_page.click(onboarding_page.button_agree_terms)

    onboarding_page.add_data_onboarding()

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.click(main_page.button_profile)

    profile_page.click(profile_page.button_logout)

    main_page.check_current_page(Url.LOGIN_PAGE)
