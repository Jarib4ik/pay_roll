import time

import allure
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class MainPage(BasePage):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

        # Локаторы элементов на главной странице
        self.page_content = (By.TAG_NAME, "body")
        self.header = (By.TAG_NAME, "header")
        self.main_container = (By.TAG_NAME, "main")
        self.email_input = (By.XPATH, "//input[@type='text']")
        self.submit_button = (By.XPATH, "//button[@type='submit']")
        self.logo = (By.XPATH, "//img[contains(@src, 'logo') or contains(@alt, 'logo')]")
        self.button_fill_address = (By.XPATH, "//div[text()='Start now']")
        self.error_invalid_otp = (By.XPATH, "//div[text()='Invalid OTP']")
        self.button_code_again = (By.XPATH, "//button[text()='Send the code again']")

        # Локаторы работника
        self.worker_show_contract = (By.XPATH, "//div[@class='ContractCard_action__aK_9S' and text()='Show']")
        self.worker_sign_contract = (By.XPATH, "//div[text()='Sign']")
        self.worker_pass_kyc_text = (By.XPATH, "//div[text()='Pass the KYC']")
        self.worker_fill_address_text = (By.XPATH, "//div[text()='Fill the address information']")
        # Альтернативные локаторы для worker_sign_contract
        self.worker_sign_contract_alt = (By.XPATH, "//button[text()='Sign'] | //div[contains(@class, 'action') and text()='Sign'] | //span[text()='Sign']")
        self.worker_review_contract = (By.XPATH, "//button[text()='Review contract']")
        self.worker_button_signing = (By.XPATH, "//button[text()='Signing']")
        self.worker_download_pdf = (By.XPATH, "//button[text()='Download PDF']")

    def is_page_opened(self):
        """Проверяет, что главная страница открыта"""
        return self.is_element_visible(self.page_content)

    @allure.step("Открытие главной страницы example-payroll.dev")
    def open_main_page(self):
        """Открывает главную страницу и проверяет её загрузку"""
        self.open_site()
        assert self.is_page_opened(), "Главная страница не открылась"
        print("Главная страница example-payroll.dev успешно открыта")

    @allure.step("Проверка наличия логотипа")
    def check_logo_present(self):
        """Проверяет наличие логотипа на странице"""
        return self.is_element_present(self.logo)

    @allure.step("Проверка наличия поля email")
    def check_email_field_present(self):
        """Проверяет наличие поля для ввода email"""
        return self.is_element_present(self.email_input)

    @allure.step("Ввод email в поле")
    def enter_email(self, email):
        """Вводит email в соответствующее поле"""
        if self.is_element_present(self.email_input):
            self.clear_and_type(self.email_input, email)
            print(f"Введен email: {email}")
        else:
            print("Поле email не найдено на странице")

    @allure.step("Клик по кнопке отправки")
    def click_submit_button(self):
        """Кликает по кнопке отправки формы"""
        if self.is_element_present(self.submit_button):
            self.click(self.submit_button)
            print("Нажата кнопка отправки")
        else:
            print("Кнопка отправки не найдена на странице")

    @allure.step("Проверка элементов главной страницы")
    def verify_main_page_elements(self):
        """Проверяет основные элементы главной страницы"""
        print("Проверка элементов главной страницы...")

        # Проверяем наличие основных элементов
        elements_check = {
            "Контент страницы": self.is_element_present(self.page_content),
            "Заголовок": self.is_element_present(self.header),
            "Основной контейнер": self.is_element_present(self.main_container)
        }

        for element_name, is_present in elements_check.items():
            if is_present:
                print(f"✓ {element_name} найден")
            else:
                print(f"✗ {element_name} не найден")

        return all(elements_check.values())

    @allure.step("Получение заголовка страницы")
    def get_page_title(self):
        """Возвращает заголовок страницы"""
        return self.driver.title

    @allure.step("Проверка заголовка страницы")
    def verify_page_title(self, expected_title=None):
        """Проверяет заголовок страницы"""
        actual_title = self.get_page_title()
        print(f"Заголовок страницы: {actual_title}")

        if expected_title:
            assert expected_title in actual_title, (
                f"Ожидался заголовок содержащий '{expected_title}', "
                f"но получен '{actual_title}'"
            )

        return actual_title

    @allure.step("Success login")
    def login(self, email):
        self.human_type(self.email_input, email.email)
        self.click(self.submit_button)
        self.add_otp_from_db(email=email.email)

    @allure.step("Клик по кнопке подписания контракта работником")
    def click_worker_sign_contract(self):
        """
        Умный клик по кнопке Sign с несколькими вариантами локаторов
        """
        try:
            # Пробуем основной и альтернативный локаторы
            self.smart_click(
                primary_locator=self.worker_sign_contract,
                alternative_locator=self.worker_sign_contract_alt
            )
        except Exception as e:
            print(f"Не удалось найти кнопку Sign: {e}")
            # Попробуем найти любую кнопку с текстом Sign на странице
            fallback_locator = (By.XPATH, "//*[contains(text(), 'Sign')]")
            try:
                print("Пробуем fallback локатор для любого элемента с текстом 'Sign'")
                self.smart_click(fallback_locator)
            except Exception as fallback_error:
                print(f"Fallback тоже не сработал: {fallback_error}")
                raise Exception(f"Не удалось найти кнопку Sign ни одним способом")

    @allure.step("Click button fill address")
    def click_fill_address_button(self):
        """Кликает по кнопке 'Start now' для заполнения адреса"""
        self.click(self.button_fill_address)
