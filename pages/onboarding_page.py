import allure
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class OnboardingPage(BasePage):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

        self.button_agree_terms = (By.XPATH, "//button[text()='Agree']")
        # Select country selectors
        self.button_select_country = (By.XPATH, "//button[text()='Country of residence']")
        self.select_country_field = (By.XPATH, "//input[@placeholder='Search country of Residence']")
        self.select_kazakhstan_country = (By.XPATH, "(//div[text()='Kazakhstan'])[1]")
        self.id_number_field = (By.XPATH, "//input[@placeholder='ID Number (passport or residence permit)']")
        # Select tax selectors
        self.button_select_tax = (By.XPATH, "//button[text()='Country of tax residence']")
        self.select_tax_field = (By.XPATH, "//input[@placeholder='Search country of TAX Residence']")
        self.select_kazakhstan_tax = (By.XPATH, "(//div[text()='Kazakhstan'])[2]")
        self.tax_number_field = (By.XPATH, "//input[@placeholder='Tax Number']")
        # Other selectors
        self.button_next = (By.XPATH, "//button[text()='Next']")

        # Локаторы метода вывода
        self.button_create_withdrawal = (By.XPATH, "//div[@class='HomeCard_action__saGEi' and text()='Create']")
        self.button_sepa_withdrawal = (By.XPATH, "//button[.//span[text()='SEPA']]")
        self.button_add_account_withdrawal = (By.XPATH, "//button[.//span[text()='Add Account']]")
        self.iban_input_field = (By.XPATH, "//input[@placeholder='IBAN']")
        self.bic_swift_input_field = (By.XPATH, "//input[@placeholder='BIC/SWIFT']")
        self.confirm_withdrawal_data = (By.XPATH, "//button[text()='Confirm']")

        self.test_withdrawal_account = (By.XPATH, "//button[.//span[contains(text(), 'IT85Y0306974823100000006843')]]")

        # Пока не используются но могут пригодиться
        self.city_field = (By.XPATH, "//input[@placeholder='City']")
        self.address_field = (By.XPATH, "//input[@placeholder='Address']")
        self.zip_field = (By.XPATH, "//input[@placeholder='Zip']")
        self.button_complete = (By.XPATH, "//button[text()='Complete']")

    @allure.step("Select Kazakhstan Federation in country list")
    def select_country(self):
        self.click(self.button_select_country)
        self.human_type(self.select_country_field, text="Kazakhstan")
        self.click(self.select_kazakhstan_country)

    @allure.step("Select Kazakhstan in tax list")
    def select_tax(self):
        self.click(self.button_select_tax)
        self.human_type(self.select_tax_field, text="Kazakhstan")
        self.click(self.select_kazakhstan_tax)

    @allure.step("Add data onboarding")
    def add_data_onboarding(self):
        self.select_country()
        self.human_type(self.id_number_field, "4844564646154253")
        self.select_tax()
        self.human_type(self.tax_number_field, "317509238590")
        self.click(self.button_next)

    @allure.step("Fill address information")
    def fill_address_info(self):
        self.human_type(self.city_field, "Bishkek")
        self.human_type(self.address_field, "st.Togolok Moldo 54a")
        self.human_type(self.zip_field, "720033")
        self.click(self.button_complete)

    @allure.step("Fill withdrawal data")
    def fill_withdrawal_data(self):
        self.human_type(self.iban_input_field, "IT85Y0306974823100000006843")
        self.human_type(self.bic_swift_input_field, "NBRKKZKX")
        self.click(self.confirm_withdrawal_data)
