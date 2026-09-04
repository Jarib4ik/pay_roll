import allure
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class ProfilePage(BasePage):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

        self.button_logout = (By.XPATH, "//button[contains(@class, 'UserProfile_logout') and text()=' Logout']")