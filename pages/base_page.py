import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from util.db.db_queries import DBQueries
from util.db.db_query import DBQuery
from util.helper import take_screenshot_name
import allure
import time as time_module
import os

from util.otp_helper import OTPHelper


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.timeout = 30
        self.otpInput = (By.XPATH, "//input[@inputmode='numeric'][{}]")

        # Menu button
        self.button_home = (By.XPATH, "//button[text()='Home' and contains(@class, 'BtnBordered_btnHeader')]")
        self.button_contracts = \
            (By.XPATH, "//button[contains(@class, 'BtnBordered_btnHeader') and contains(text(), 'Contracts')]")
        self.button_profile = (By.XPATH, "//button[text()='Profile' and contains(@class, 'BtnBordered_btnHeader')]")

    @allure.step("Открытие страницы")
    def open_page(self, url=""):
        """Открывает страницу"""
        if url.startswith("http"):
            full_url = url
        else:
            full_url = f"{self.base_url}{url}"

        with allure.step(f"Открытие страницы: {full_url}"):
            self.driver.get(full_url)
            self.wait_page_load()
        print(f"Открыта страница: {full_url}")

    @allure.step("Открытие главной страницы")
    def open_site(self):
        """Открывает главную страницу сайта"""
        return self.driver.get(self.base_url)

    @allure.step("Check current url with expected")
    def check_current_page(self, url_enum):
        self.wait_page_load()
        exp_url = f"{self.base_url}{url_enum.value}"

        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: driver.current_url == exp_url
        )

        curr_url = self.driver.current_url

        assert curr_url == exp_url, (
            f"Wrong page. Expected: {exp_url}, " f"Current page: {curr_url}"
        )

    def find_element(self, locator):
        """Находит элемент на странице"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Не удалось найти элемент по локатору {locator}",
        )

    def find_elements(self, locator):
        """Находит несколько элементов на странице"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(locator),
            message=f"Не удалось найти элементы по локатору {locator}",
        )

    def is_element_present(self, locator):
        """Проверяет наличие элемента на странице"""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            print(f"Элемент {locator} не найден")
            return False
        finally:
            self.take_screenshot(str(locator), "Проверка наличия элемента")

    def is_element_visible(self, locator):
        """Проверяет видимость элемента на странице"""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element.is_displayed()
        except TimeoutException:
            return False

    @allure.step("Проверка видимости элемента")
    def check_element_visible(self, locator, timeout=None):
        """Проверяет что элемент видим и ждет его появления"""
        if timeout is None:
            timeout = self.timeout
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator),
                message=f"Элемент {locator} не стал видимым за {timeout} секунд"
            )
            print(f"✅ Элемент {locator} видим")
            return element
        except TimeoutException as e:
            print(f"❌ Элемент {locator} не стал видимым за {timeout} секунд")
            # Делаем скриншот для отладки
            try:
                self.take_screenshot(str(locator), "Элемент не найден")
            except:
                pass
            raise e

    @allure.step("Клик по элементу")
    def click(self, locator, pre_click_delay=0.3, post_click_delay=0.2):
        """Кликает по элементу с задержками"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )

        # Прокрутка к элементу
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

        time_module.sleep(pre_click_delay)
        element.click()
        time_module.sleep(post_click_delay)

    @allure.step("Быстрый клик")
    def force_click(self, locator):
        """Быстрый клик без задержек"""
        return (
            WebDriverWait(self.driver, self.timeout)
            .until(
                EC.element_to_be_clickable(locator),
                message=f"Элемент {locator} не кликабелен",
            )
            .click()
        )

    @allure.step("JavaScript клик")
    def js_click(self, locator):
        """Клик через JavaScript для обхода перекрывающих элементов"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Элемент {locator} не найден для JS клика"
        )
        
        # Прокрутка к элементу
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # JavaScript клик
        self.driver.execute_script("arguments[0].click();", element)
        print(f"Выполнен JavaScript клик по элементу: {locator}")
        time.sleep(0.3)

    @allure.step("Умный клик с несколькими локаторами")
    def smart_click(self, primary_locator, alternative_locator=None, timeout=None):
        """
        Пробует кликнуть по элементу, используя основной локатор,
        если не получается - пробует альтернативный
        """
        if timeout is None:
            timeout = self.timeout
            
        try:
            print(f"Пробуем основной локатор: {primary_locator}")
            self.click(primary_locator)
            return True
        except Exception as e1:
            print(f"Основной локатор не сработал: {e1}")
            
            if alternative_locator:
                try:
                    print(f"Пробуем альтернативный локатор: {alternative_locator}")
                    self.click(alternative_locator)
                    return True
                except Exception as e2:
                    print(f"Альтернативный локатор не сработал: {e2}")
                    
                    # Последняя попытка - JavaScript клик на любой найденный элемент
                    try:
                        print("Пробуем JavaScript клик на основной локатор...")
                        self.js_click(primary_locator)
                        return True
                    except Exception as e3:
                        try:
                            print("Пробуем JavaScript клик на альтернативный локатор...")
                            self.js_click(alternative_locator)
                            return True
                        except Exception as e4:
                            print(f"Все попытки клика не удались. Ошибки:")
                            print(f"1. Основной клик: {e1}")
                            print(f"2. Альтернативный клик: {e2}")
                            print(f"3. JS клик основной: {e3}")
                            print(f"4. JS клик альтернативный: {e4}")
                            raise Exception(f"Не удалось кликнуть ни по одному из локаторов")
            else:
                # Пробуем JavaScript клик
                try:
                    print("Пробуем JavaScript клик...")
                    self.js_click(primary_locator)
                    return True
                except Exception as e2:
                    print(f"JavaScript клик тоже не сработал: {e2}")
                    raise Exception(f"Все попытки клика не удались: {e1}, {e2}")

    @allure.step("Ввод текста")
    def type_text(self, locator, text):
        """Вводит текст в поле"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )
        element.send_keys(text)

    @allure.step("Очистка поля и ввод текста")
    def clear_and_type(self, locator, text):
        """Очищает поле и вводит новый текст"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )
        element.clear()
        element.send_keys(text)

    @allure.step("Плавный ввод текста")
    def human_type(self, locator, text, min_delay=0.05, max_delay=0.15):
        """Имитирует человеческий ввод текста с задержками"""
        import random

        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

        for char in text:
            element.send_keys(char)
            delay = random.uniform(min_delay, max_delay)
            time_module.sleep(delay)

    def get_element_text(self, locator):
        """Получает текст элемента"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element.text

    def check_element_text(self, locator, expected_text):
        """Проверяет текст элемента"""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            actual_text = element.text
            assert actual_text == expected_text, (
                f"Ожидался текст '{expected_text}', но найден '{actual_text}'"
            )
        except TimeoutException:
            assert False, f"Элемент {locator} не виден на странице"

    def check_element_visible(self, locator):
        """Проверяет, что элемент виден"""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            assert False, f"Элемент {locator} не виден"

    def check_element_not_visible(self, locator):
        """Проверяет, что элемент не виден"""
        try:
            WebDriverWait(self.driver, self.timeout).until_not(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            assert False, f"Элемент {locator} все еще виден"

    @allure.step("Ожидание загрузки страницы")
    def wait_page_load(self):
        """Ожидает полной загрузки страницы"""
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    @allure.step("Обновление страницы")
    def refresh_page(self, wait_for_load=True):
        """Обновляет текущую страницу"""
        self.driver.refresh()
        if wait_for_load:
            self.wait_page_load()

    @allure.step("Создание скриншота")
    def take_screenshot(self, page_name: str, action: str) -> None:
        """Создает скриншот с указанным именем"""
        try:
            screenshot_name = take_screenshot_name(page_name, action)
            screenshots_dir = "screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            screenshot_path = os.path.join(screenshots_dir, screenshot_name)
            self.driver.save_screenshot(screenshot_path)

            # Прикрепляем скриншот к отчету Allure
            with open(screenshot_path, "rb") as image_file:
                allure.attach(
                    image_file.read(),
                    name=f"{page_name} - {action}",
                    attachment_type=allure.attachment_type.PNG
                )
        except Exception as e:
            print(f"Ошибка при создании скриншота: {e}")

    @allure.step("Клик по пустой области")
    def click_empty_area(self):
        """Кликает по пустой области страницы"""
        body = self.find_element((By.TAG_NAME, "body"))
        body.click()

    @allure.step("Очистка поля")
    def clear_field(self, locator):
        """Очищает поле ввода"""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )
        element.clear()

    def get_current_url(self):
        """Возвращает текущий URL"""
        return self.driver.current_url

    def scroll_to_element(self, locator):
        """Прокручивает страницу к элементу"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_bottom(self):
        """Прокручивает страницу вниз"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        """Прокручивает страницу вверх"""
        self.driver.execute_script("window.scrollTo(0, 0);")

    @allure.step("Получение и ввод OTP кода из базы данных")
    def add_otp_from_db(self, email):
        """
        Получает OTP секретный ключ из БД и генерирует актуальный OTP код

        Args:
            email: Email пользователя для поиска в БД
        """
        params = (email,)
        db_query = DBQuery()
        try:
            # Получаем секретный ключ из базы данных
            otp_secret = db_query.get_single_string_column_from_query(
                DBQueries.get_auth_otp_by_email(), params
            )

            if otp_secret:
                print(f"Получен OTP секретный ключ: {otp_secret[:8]}...")

                # Генерируем актуальный OTP код из секретного ключа
                otp_code = OTPHelper.generate_otp_from_secret(otp_secret, interval=600)
                print(f"Сгенерирован OTP код: {otp_code}")

                # Убираем дефис для ввода в поля
                clean_otp_code = OTPHelper.clean_otp_code(otp_code)

                # Вводим код в поля на странице
                self.type_otp_mode_input(clean_otp_code)

                return otp_code
            else:
                raise Exception("Не удалось получить OTP секретный ключ из базы данных")

        except Exception as e:
            print(f"Ошибка при получении OTP кода: {e}")
            raise e

    @allure.step("Получаем OTP код для подписи менеджером и вводим")
    def get_manager_otp_and_add(self, email: str):
        params = (email,)
        db_query = DBQuery()

        try:
            # Получаем ID пользователя
            user_id = db_query.get_single_string_column_from_query(
                DBQueries.get_user_id_by_email(), params
            )

            if not user_id:
                print(f"Пользователь с email '{email}' не найден")
                return False

            contract_id = db_query.get_single_string_column_from_query(
                DBQueries.get_contract_id_by_manager(), (user_id,)
            )

            if not contract_id:
                raise Exception(f"Не удалось найти контракт для менеджера с ID {user_id}")

            otp_code = db_query.get_single_string_column_from_query(
                DBQueries.get_manager_signature_otp_by_contract_id(), (contract_id,)
            )

            self.type_otp_mode_input(otp_code)

            if not otp_code:
                raise Exception(f"Не удалось получить OTP код для контракта с ID {contract_id}")

            return otp_code

        except Exception as e:
            print(f"Ошибка при получении OTP кода для менеджера: {e}")
            raise e

    @allure.step("Получаем OTP код для подписи работником и вводим")
    def get_worker_otp_and_add(self, email: str):
        params = (email,)
        db_query = DBQuery()

        try:
            # Получаем ID пользователя
            user_id = db_query.get_single_string_column_from_query(
                DBQueries.get_user_id_by_email(), params
            )

            if not user_id:
                print(f"Пользователь с email '{email}' не найден")
                return False

            contract_id = db_query.get_single_string_column_from_query(
                DBQueries.get_contract_id_by_worker(), (user_id,)
            )

            if not contract_id:
                raise Exception(f"Не удалось найти контракт для работника с ID {user_id}")

            otp_code = db_query.get_single_string_column_from_query(
                DBQueries.get_worker_signature_otp_by_contract_id(), (contract_id,)
            )

            self.type_otp_mode_input(otp_code)

            if not otp_code:
                raise Exception(f"Не удалось получить OTP код для контракта с ID {contract_id}")

            return otp_code

        except Exception as e:
            print(f"Ошибка при получении OTP кода для работника: {e}")
            raise e

    @allure.step("Ввод OTP кода в поля")
    def type_otp_mode_input(self, text):
        """
        Вводит OTP код в отдельные поля ввода

        Args:
            text: OTP код из 6 цифр
        """
        if len(text) == 6:
            print(f"Ввод OTP кода: {text}")
            self.wait_page_load()
            time.sleep(3)

            # Вводим каждую цифру в отдельное поле
            for i in range(6):
                field_number = i + 1
                locator = (self.otpInput[0], self.otpInput[1].format(field_number))
                self.human_type(locator, text[i])

            self.wait_page_load()
            print("OTP код успешно введен")
        else:
            raise ValueError(f"OTP код должен содержать 6 цифр, получено: {len(text)} символов")

    @allure.step("Approve KYC")
    def approve_kyc(self, email: str):
        db_query = DBQuery()
        success = db_query.set_user_kyc_status_by_email(email)
        return success

    @allure.step("Закрытие всех вкладок кроме первой")
    def close_all_tabs_except_first(self):
        """
        Закрывает все открытые вкладки браузера кроме первой.
        Возвращается к первой вкладке после закрытия остальных.
        """
        try:
            # Получаем все открытые вкладки
            all_handles = self.driver.window_handles
            print(f"Текущие handles вкладок: {all_handles}")

            if len(all_handles) <= 1:
                print("Открыта только одна вкладка, нечего закрывать")
                return

            # Сохраняем handle первой вкладки
            first_tab = all_handles[0]
            print(f"Первая вкладка (сохраняем): {first_tab}")

            print(f"Найдено {len(all_handles)} вкладок. Закрываем все кроме первой...")

            # Закрываем все вкладки кроме первой (в обратном порядке для стабильности)
            for handle in reversed(all_handles[1:]):
                try:
                    print(f"Переключаемся на вкладку для закрытия: {handle}")
                    self.driver.switch_to.window(handle)
                    
                    # Небольшая пауза для стабильности
                    time.sleep(0.5)
                    
                    print(f"Закрываем вкладку: {handle}")
                    self.driver.close()
                    
                    # Проверяем что вкладка действительно закрылась
                    remaining_handles = self.driver.window_handles
                    if handle in remaining_handles:
                        print(f"⚠️ Вкладка {handle} не закрылась, пробуем ещё раз...")
                        time.sleep(1)
                        if handle in self.driver.window_handles:
                            print(f"❌ Не удалось закрыть вкладку {handle}")
                    else:
                        print(f"✅ Вкладка {handle} успешно закрыта")
                        
                except Exception as tab_error:
                    print(f"Ошибка при закрытии вкладки {handle}: {tab_error}")

            # Переключаемся обратно на первую вкладку
            try:
                print(f"Переключаемся обратно на первую вкладку: {first_tab}")
                self.driver.switch_to.window(first_tab)
                
                # Проверяем что мы действительно на первой вкладке
                current_handle = self.driver.current_window_handle
                if current_handle == first_tab:
                    print("✅ Успешно переключились на первую вкладку")
                else:
                    print(f"⚠️ Текущая вкладка {current_handle} не совпадает с ожидаемой {first_tab}")
                    
            except Exception as switch_error:
                print(f"Ошибка при переключении на первую вкладку: {switch_error}")
                # Пробуем переключиться на любую доступную вкладку
                try:
                    available_handles = self.driver.window_handles
                    if available_handles:
                        self.driver.switch_to.window(available_handles[0])
                        print(f"Переключились на доступную вкладку: {available_handles[0]}")
                except:
                    pass

            # Финальная проверка
            final_handles = self.driver.window_handles
            print(f"Итоговое количество вкладок: {len(final_handles)}")
            print(f"Итоговые handles: {final_handles}")

        except Exception as e:
            print(f"❌ Критическая ошибка при закрытии вкладок: {e}")
            # В случае ошибки пытаемся переключиться на первую доступную вкладку
            try:
                available_handles = self.driver.window_handles
                if available_handles:
                    self.driver.switch_to.window(available_handles[0])
                    print(f"Аварийное переключение на вкладку: {available_handles[0]}")
            except Exception as emergency_error:
                print(f"Не удалось выполнить аварийное переключение: {emergency_error}")
