import pytest
from pages.main_page import MainPage
from pages.contract_page import ContractPage
from pages.onboarding_page import OnboardingPage
from pages.profile_page import ProfilePage
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os
from config.config import DEFAULT_BASE_URL, BROWSER_OPTIONS

# Загружаем переменные окружения
load_dotenv()


def pytest_addoption(parser):
    """Добавляет параметры командной строки для pytest"""
    parser.addoption(
        "--base-url",
        action="store",
        default=DEFAULT_BASE_URL,
        help=f"Base URL for the tests (default: {DEFAULT_BASE_URL})",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode (default: False)",
    )
    parser.addoption(
        "--local",
        action="store_true",
        default=False,
        help="Run tests with local database connection (default: False)",
    )


@pytest.fixture(scope="session")
def base_url(request):
    """Фикстура для получения базового URL"""
    return request.config.getoption("--base-url") or DEFAULT_BASE_URL


@pytest.fixture(scope="session")
def is_headless(request):
    """Фикстура для определения режима headless"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="session")
def is_local_run(request):
    """Фикстура для определения типа запуска (локальный или удаленный)"""
    return request.config.getoption("--local")


@pytest.fixture
def api_client():
    """
    Фикстура для создания неавторизованного API клиента
    """
    from api.api_client import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client():
    """
    Фикстура для создания авторизованного API клиента
    
    ВНИМАНИЕ: Для реального использования требуется действующий токен
    """
    from api.api_client import APIClient
    
    # Используем тестовый токен для моков или задаем через переменную окружения
    test_token = os.getenv("TEST_API_TOKEN", "test_token_for_mocks")
    
    client = APIClient(token=test_token)
    return client


@pytest.fixture(scope="function")
def browser(base_url, request, is_headless):
    """Фикстура для создания экземпляра браузера"""
    options = webdriver.ChromeOptions()
    
    # Добавляем базовые опции браузера
    for option, value in BROWSER_OPTIONS.items():
        if value and option != "headless":
            option_name = f"--{option.replace('_', '-')}"
            options.add_argument(option_name)
    
    # Добавляем headless режим если указан
    if is_headless or BROWSER_OPTIONS.get("headless", False):
        options.add_argument("--headless")
        # Дополнительные опции для стабильности в CI headless режиме
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--disable-blink-features=AutomationControlled")
        print("Запуск в headless режиме с дополнительными опциями стабильности")
    
    # Проверяем, запущены ли тесты локально
    run_local = request.config.getoption("--local")
    
    # Определяем путь к ChromeDriver
    chromedriver_path = None
    
    try:
        if run_local:
            # Локальный запуск - используем webdriver-manager для автоматической совместимости версий
            print("Локальный запуск: используем webdriver-manager для автоматического управления версиями")
            from webdriver_manager.chrome import ChromeDriverManager
            chromedriver_path = ChromeDriverManager().install()
        else:
            # Удаленный запуск - используем установленный ChromeDriver
            options.add_argument("--headless")  # Принудительно headless для удаленного запуска
            chromedriver_path = "/usr/local/bin/chromedriver"
            
            # Если путь не существует, попробуем brew версию
            if not os.path.exists(chromedriver_path):
                chromedriver_path = "/opt/homebrew/bin/chromedriver"
        
        if not chromedriver_path or not os.path.exists(chromedriver_path):
            print("ChromeDriver не найден, используем webdriver-manager в качестве fallback")
            from webdriver_manager.chrome import ChromeDriverManager
            chromedriver_path = ChromeDriverManager().install()
            
        print(f"Используем ChromeDriver: {chromedriver_path}")
        
        service = Service(executable_path=chromedriver_path)
        
        # Создаем драйвер
        driver = webdriver.Chrome(options=options, service=service)
        driver.maximize_window()
        
        # Настраиваем таймауты для стабильности (особенно важно для CI)
        driver.implicitly_wait(15)  # Увеличено для CI окружения
        driver.set_page_load_timeout(120)  # Увеличено для медленных CI серверов  
        driver.set_script_timeout(60)  # Увеличено для сложных скриптов
        
        yield driver
        
    except Exception as e:
        print(f"Ошибка при создании браузера: {e}")
        print("Пробуем использовать webdriver-manager в качестве последней попытки...")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            chromedriver_path = ChromeDriverManager().install()
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(options=options, service=service)
            driver.maximize_window()
            
            # Настраиваем таймауты для стабильности (fallback режим)
            driver.implicitly_wait(15)
            driver.set_page_load_timeout(120)
            driver.set_script_timeout(60)
            
            yield driver
        except Exception as fallback_error:
            raise Exception(f"Не удалось запустить браузер: {e}. Fallback ошибка: {fallback_error}")
    
    # Очистка после теста
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        print("Данные браузера очищены")
    except Exception as e:
        print(f"Ошибка при очистке данных браузера: {e}")
    
    driver.quit()


@pytest.fixture(scope="function")
def main_page(browser, base_url):
    """Фикстура для создания экземпляра главной страницы"""
    return MainPage(browser, base_url)


@pytest.fixture(scope="function")
def contract_page(browser, base_url):
    """Фикстура для создания экземпляра страницы контрактов"""
    return ContractPage(browser, base_url)


@pytest.fixture(scope="function")
def onboarding_page(browser, base_url):
    """Фикстура для создания экземпляра страницы онбординга"""
    return OnboardingPage(browser, base_url)

@pytest.fixture(scope="function")
def profile_page(browser, base_url):
    """Фикстура для создания экземпляра страницы профиля"""
    return ProfilePage(browser, base_url)


@pytest.fixture(scope="function", autouse=True)
def test_setup(request):
    """Автоматическая фикстура для логирования начала и окончания тестов"""
    test_name = request.node.name
    print(f"\n{'='*60}")
    print(f"Начало теста: {test_name}")
    print(f"{'='*60}")
    
    yield
    
    print(f"\n{'='*60}")
    print(f"Окончание теста: {test_name}")
    print(f"{'='*60}\n")


@pytest.fixture(scope="session")
def clean_db_after_session():
    """
    Фикстура для удаления данных пользователей из БД после завершения всей сессии тестов.
    Поддерживает добавление как отдельных email, так и списков email.

    Использование:
    def test_example(clean_db_after_session):
        # Добавить один email
        clean_db_after_session("test@example.com")

        # Добавить список email
        clean_db_after_session(["user1@test.com", "user2@test.com"])

        # Добавить объект пользователя
        clean_db_after_session(TEST_USER.email)
    """
    # Множество email для очистки данных (используем set для избежания дубликатов)
    emails_to_clean = set()

    def _add_emails(emails):
        """
        Добавляет email(ы) в список для очистки.

        :param emails: str, list, tuple или объект с атрибутом email
        """
        if isinstance(emails, (list, tuple)):
            # Если передан список/кортеж email
            for email in emails:
                if hasattr(email, 'email'):
                    # Если это объект пользователя с атрибутом email
                    emails_to_clean.add(email.email)
                elif isinstance(email, str):
                    # Если это строка с email
                    emails_to_clean.add(email)
                else:
                    print(f"ПРЕДУПРЕЖДЕНИЕ: Неизвестный тип для email: {type(email)}")
        elif isinstance(emails, str):
            # Если передан один email как строка
            emails_to_clean.add(emails)
        elif hasattr(emails, 'email'):
            # Если передан объект пользователя с атрибутом email
            emails_to_clean.add(emails.email)
        else:
            print(f"ПРЕДУПРЕЖДЕНИЕ: Неизвестный тип для emails: {type(emails)}")

        print(f"Добавлено в очередь на удаление. Всего email: {len(emails_to_clean)}")

    yield _add_emails  # Возвращаем функцию для добавления email

    # После завершения всех тестов удаляем данные для всех добавленных email
    if not emails_to_clean:
        print("Нет email для очистки.")
        return

    print(f"🚀 Начинаем каскадную очистку данных для {len(emails_to_clean)} пользователей")

    try:
        # Используем DBQuery для каскадного удаления
        from util.db.db_query import DBQuery
        
        db_query = DBQuery()
        failed_cleanups = []
        successful_cleanups = 0

        for email in emails_to_clean:
            try:
                print(f"Каскадное удаление данных для: {email}")
                success = db_query.delete_user_cascade_by_email(email, dry_run=False)
                if success:
                    successful_cleanups += 1
                    print(f"✅ Данные для {email} успешно удалены")
                else:
                    failed_cleanups.append(f"Ошибка при удалении {email}")
                    print(f"❌ Ошибка при удалении данных для {email}")
            except Exception as e:
                error_msg = f"❌ Ошибка при удалении данных для {email}: {e}"
                print(error_msg)
                failed_cleanups.append(error_msg)

        # Выводим итоговую статистику
        print("\n📊 Итоги каскадной очистки:")
        print(f"✅ Успешно очищено: {successful_cleanups}")
        print(f"❌ Ошибок: {len(failed_cleanups)}")

        if failed_cleanups:
            print("\n🚨 Детали ошибок:")
            for error in failed_cleanups:
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Критическая ошибка при каскадной очистке: {e}")
        print("📋 Список email для ручной очистки:")
        for email in emails_to_clean:
            print(f"  - {email}")