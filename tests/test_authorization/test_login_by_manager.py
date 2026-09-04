import pytest
import allure

from data.url import Url
from data.users import MANAGER


@pytest.mark.smoke
@allure.feature("Authorization")
@allure.title("Success Auth")
@allure.description("Add manager email to field, add OTP and success auth")
def test_login_by_manager(main_page):
    
    main_page.open_main_page()
    
    main_page.login(email=MANAGER)

    main_page.check_current_page(Url.MAIN_PAGE)
