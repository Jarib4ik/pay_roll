import pytest
import allure

from data.url import Url
from data.users import TEST_LOGIN


@pytest.mark.smoke
@allure.feature("Authorization")
@allure.title("Success Auth")
@allure.description("Add email to field, add OTP and success auth")
def test_login(main_page):
    
    main_page.open_main_page()
    
    main_page.login(email=TEST_LOGIN)

    main_page.check_current_page(Url.ONBOARDING_PAGE)
