import time

import pytest
import allure

from data.url import Url
from data.users import TEST_LOGIN


@pytest.mark.smoke
@allure.feature("Authorization")
@allure.title("Wrong OTP")
@allure.description("Add email to field, add wrong OTP")
def test_wrong_otp(main_page):

    main_page.open_main_page()

    main_page.human_type(main_page.email_input, TEST_LOGIN.email)

    main_page.click(main_page.submit_button)

    main_page.type_otp_mode_input("555555")

    main_page.check_element_visible(main_page.error_invalid_otp)
