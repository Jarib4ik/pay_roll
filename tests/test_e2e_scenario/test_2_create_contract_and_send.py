import time

import pytest
import allure

from data.url import Url
from data.users import MANAGER, TEST_WORKER


@pytest.mark.smoke
@allure.feature("Create contract by manager")
@allure.title("Create contract")
@allure.description("Success auth and create new contract")
def test_create_contract_and_send(main_page, contract_page, clean_db_after_session):
    
    main_page.open_main_page()
    
    main_page.login(email=MANAGER)

    main_page.check_current_page(Url.MAIN_PAGE)

    main_page.click(main_page.button_contracts)

    main_page.wait_page_load()

    main_page.wait_page_load()

    contract_page.click(contract_page.button_create_contract)

    contract_page.add_contract_data(email=TEST_WORKER.email)

    time.sleep(5)

    contract_page.click_contract_by_email(email=TEST_WORKER.email)

    contract_page.click(contract_page.send_invite)

    main_page.wait_page_load()

    time.sleep(5)

    contract_page.refresh_page()

    contract_page.click_contract_by_email(email=TEST_WORKER.email)

    contract_page.click(contract_page.sign_by_manager)

    contract_page.get_manager_otp_and_add(email=MANAGER.email)

