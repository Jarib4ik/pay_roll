import allure
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class ContractPage(BasePage):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

        self.button_create_contract = \
            (By.XPATH, "//button[text()='Create contract']")

        # Create contract form
        self.contract_email_field = \
            (By.XPATH, "//div[contains(@class, 'Input_wrapper') and .//div[text()='Email']]//input")
        self.contract_first_name_field = \
            (By.XPATH, "//div[contains(@class, 'Input_wrapper') and .//div[text()='First name']]//input")
        self.contract_last_name_field = \
            (By.XPATH, "//div[contains(@class, 'Input_wrapper') and .//div[text()='Last name']]//input")
        self.contract_project_name_field = \
            (By.XPATH, "//div[contains(@class, 'Input_wrapper') and .//div[text()='Project name']]//input")
        self.contract_scope_of_services_field = \
            (By.XPATH, "//div[contains(@class, 'Textarea_wrapper') and .//div[text()='Scope of services']]//textarea")
        self.button_create_in_form = (By.XPATH, "//button[text()='Create' and @type='submit']")
        self.button_contract_template = (By.XPATH, "//button[text()='Contract template']")
        self.button_service_agreement = (By.XPATH, "//div[text()='Service agreement']")

        self.send_invite = (By.XPATH, "//button[contains(@class, 'Btn_btn') and text()='Send invite']")
        self.sign_by_manager = (By.XPATH, "//button[text()='Signing']")

    @allure.step("Add contract data")
    def add_contract_data(self, email):
        self.human_type(self.contract_email_field, text=email)
        self.human_type(self.contract_first_name_field, text='TEST first name')
        self.human_type(self.contract_last_name_field, text='TEST last name')
        self.human_type(self.contract_project_name_field, text='TEST project name')
        self.human_type(self.contract_scope_of_services_field, text='TEST scope of services')
        self.click(self.button_create_in_form)

    @allure.step("Click contract by email")
    def click_contract_by_email(self, email):
        # locator = (By.XPATH, f"//span[text()='{email}']")
        locator = (By.XPATH, "//td[.//span[text()='Test Testov']]")
        self.check_element_visible(locator)
        
        # Используем JavaScript клик для обхода перекрывающих элементов
        try:
            self.click(locator)
        except Exception as e:
            print(f"Обычный клик не сработал: {e}")
            print("Пробуем JavaScript клик...")
            self.js_click(locator)

    @allure.step("Send invite")
    def send_invite(self):
        self.click(self.send_invite)

    @allure.step("Sign contract by manager")
    def sign_by_manager(self):
        self.click(self.sign_by_manager)


