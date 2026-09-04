import time

import pytest
import allure

from data.url import Url
from data.users import TEST_WORKER


@pytest.mark.smoke
@allure.feature("Sign by worker^")
@allure.title("Create contract")
@allure.description("Success auth and create new contract")
def test_sign_by_worker(main_page, onboarding_page, clean_db_after_session):

    clean_db_after_session(TEST_WORKER.email)

    main_page.open_main_page()

    main_page.login(email=TEST_WORKER)

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.click(main_page.worker_sign_contract)

    main_page.click(main_page.worker_review_contract)

    main_page.close_all_tabs_except_first()

    main_page.click(main_page.worker_button_signing)

    main_page.get_worker_otp_and_add(email=TEST_WORKER.email)

    main_page.check_current_page(Url.MAIN_PAGE)

    time.sleep(5)
