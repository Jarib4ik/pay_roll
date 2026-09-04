import pytest
import allure

from data.url import Url
from data.users import WRONG_EMAIL


@pytest.mark.smoke
@allure.feature("Authorization")
@allure.title("Wrong email")
@allure.description("Add wrong email to field")
def test_wrong_email(main_page):

    main_page.open_main_page()

    main_page.human_type(main_page.email_input, WRONG_EMAIL.email)

    main_page.check_element_not_visible(main_page.submit_button)
