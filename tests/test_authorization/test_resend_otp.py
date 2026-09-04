import time

import pytest
import allure

from data.url import Url
from data.users import TEST_LOGIN


@pytest.mark.smoke
@allure.feature("Authorization")
@allure.title("Click resend OTP and auth")
@allure.description("Add email to field, wait 5 min add OTP and success auth")
def test_resend_otp(main_page):

    main_page.open_main_page()

    main_page.human_type(main_page.email_input, TEST_LOGIN.email)

    main_page.click(main_page.submit_button)

    time.sleep(340)

    main_page.click(main_page.button_code_again)

    main_page.add_otp_from_db(TEST_LOGIN.email)

    main_page.check_current_page(Url.ONBOARDING_PAGE)
