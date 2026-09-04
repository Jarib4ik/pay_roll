# Pay-roll Autotests

## Описание
Автоматизированные тесты для системы pay-roll с поддержкой API example-payroll.dev.

**⚠️ ОБНОВЛЕНИЕ:** API клиент был обновлен согласно реальной документации example-payroll.dev!

## Новые API методы

### 🔐 Авторизация через OTP
- `send_otp(email)` - Отправка OTP кода на email
- `verify_otp(email, otp)` - Проверка OTP и получение токенов
- `refresh_token(refresh_token)` - Обновление access токена
- `logout(refresh_token)` - Выход из системы

### 👤 Профиль
- `get_profile(user_id)` - Получение профиля пользователя по ID
- `update_profile(user_id, data)` - Обновление профиля пользователя
- `accept_terms_and_policy(user_id)` - Согласие с условиями

### 🏢 Компании
- `get_companies()` - Список компаний пользователя
- `get_company_by_id(company_id)` - Получение компании по ID
- `create_contract_for_company(company_id, data)` - Создание контракта для компании

### 📄 Контракты
- `get_contracts()` - Список контрактов пользователя
- `get_contract_by_id(contract_id)` - Получение контракта по ID
- `update_contract(contract_id, data)` - Обновление контракта
- `sign_contract_otp(contract_id)` - Запрос OTP для подписания
- `sign_contract_otp_verify(contract_id, otp)` - Подписание контракта через OTP
- `get_contract_document_link(contract_id)` - Ссылка на документ
- `get_contract_template_example(contract_id)` - Пример шаблона
- `add_withdraw_method_to_contract(contract_id, data)` - Добавление метода вывода
- `validate_contract_signature(contract_id, file)` - Валидация подписи

### 📝 Шаблоны контрактов
- `get_contract_templates()` - Список шаблонов
- `create_contract_template(data)` - Создание шаблона
- `add_fields_to_template(template_id, fields)` - Добавление полей к шаблону

### 📋 Акты (Receipts)
- `get_receipts()` - Список актов
- `get_receipt_exhibit(receipt_id)` - Приложение к акту
- `sign_receipt_otp(receipt_id)` - Запрос OTP для подписания акта
- `sign_receipt_otp_verify(receipt_id, otp, withdraw_method_id)` - Подписание акта

### 💳 Методы вывода
- `get_withdraw_methods()` - Доступные методы вывода
- `add_user_withdraw_method(method_id, data)` - Добавление метода пользователя
- `get_user_withdraw_methods()` - Методы вывода пользователя

### 🌍 Служебные методы
- `get_countries()` - Список стран
- `get_sumsub_access_token()` - Токен для SumSub (KYC)

### 👨‍💼 Административные методы
- `manager_get_contracts()` - Контракты (для менеджеров)
- `manager_get_receipts()` - Акты (для менеджеров)
- `manager_send_contract(data)` - Отправка контракта
- `manager_update_contract(data)` - Обновление контракта

### 🔄 Legacy методы (для совместимости)
- `login(email, password)` - ⚠️ Только отправляет OTP! Используйте `verify_otp()` для завершения
- `partial_update_profile(user_id, data)` - Алиас для `update_profile()`

## Структура проекта

```
pay-roll_autotests/
├── api/
│   └── api_client.py          # API клиент example-payroll.dev
├── config/
│   └── config.py              # Конфигурация браузера и URL
├── data/
│   ├── bank_account.py        # Тестовые данные банковских счетов
│   ├── url.py                 # URL адреса и маршруты
│   └── users.py               # Тестовые пользователи
├── docs/
│   └── api_examples.md        # 📚 Примеры использования API
├── pages/
│   ├── base_page.py           # Базовая страница с улучшенными методами клика
│   ├── contract_page.py       # Страница работы с контрактами
│   ├── main_page.py           # Главная страница
│   └── onboarding_page.py     # Страница онбординга
├── tests/
│   ├── test_e2e_scenario/     # 🎭 End-to-End сценарии
│   │   ├── test_1_worker_add_data_and_signature.py
│   │   ├── test_2_create_contract_and_send.py
│   │   └── test_3_sign_by_worker.py
│   ├── skip_test_api_basic.py # 🧪 Базовые API тесты (отключены)
│   ├── skip_test_api.py       # 🌐 Интеграционные API тесты (отключены)
│   ├── test_login.py          # 🔐 Тесты авторизации UI
│   └── test_login_by_manager.py # 👨‍💼 Тесты авторизации менеджера
├── util/
│   ├── db/                    # 🗄️ Утилиты работы с PostgreSQL
│   │   ├── __init__.py
│   │   ├── db_queries.py      # SQL запросы с каскадным удалением
│   │   ├── db_query.py        # Класс для выполнения запросов
│   │   └── db_service.py      # Сервис БД
│   ├── helper.py              # Вспомогательные функции
│   └── otp_helper.py          # Работа с OTP (TOTP)
├── screenshots/               # 📸 Скриншоты тестов
├── allure-results/            # 📊 Результаты Allure отчетов
├── conftest.py                # Фикстуры pytest с улучшенным браузером
├── pytest.ini                # Настройки pytest с маркерами
├── requirements.txt           # Основные зависимости
├── requirements-dev.txt       # Зависимости разработки
└── .venv/                     # Виртуальное окружение Python
```

## Быстрый старт

### 1. Создание виртуального окружения
```bash
# Создаем виртуальное окружение
python3 -m venv .venv

# Активируем его
# На macOS/Linux:
source .venv/bin/activate
# На Windows:
# .venv\Scripts\activate
```

### 2. Установка зависимостей
```bash
# Основные зависимости
pip install -r requirements.txt

# Зависимости разработки (опционально)
pip install -r requirements-dev.txt
```

### 3. Проверка установки ChromeDriver
```bash
# Проверяем версию Chrome
google-chrome --version
# или на macOS:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Обновляем ChromeDriver при необходимости
brew upgrade chromedriver  # macOS
```

### 4. Настройка переменных окружения
```bash
export API_BASE_URL="https://api.example-payroll.dev"
export API_TOKEN="your_jwt_token"  # опционально
export TEST_API_TOKEN="test_token_for_mocks"  # для моков

# Для headless режима в CI
export HEADLESS=true
```

## Запуск тестов

### 🌐 API тесты (в разработке)
```bash
# Быстрые базовые тесты (с моками) - отключены
# pytest tests/skip_test_api_basic.py -v

# Интеграционные тесты (требуют настоящего API) - отключены  
# pytest tests/skip_test_api.py -v

# Все API тесты
# pytest -m api -v
```

### 🖥️ UI тесты
```bash
# Тест авторизации работника
pytest tests/test_login.py -v

# Тест авторизации менеджера
pytest tests/test_login_by_manager.py -v

# Запуск с видимым браузером (по умолчанию)
pytest tests/test_login.py -v

# Запуск в headless режиме
HEADLESS=true pytest tests/test_login.py -v
```

### 🎭 End-to-End сценарии
```bash
# Полный сценарий: добавление данных работника и подпись
pytest tests/test_e2e_scenario/test_1_worker_add_data_and_signature.py -v

# Создание контракта и отправка
pytest tests/test_e2e_scenario/test_2_create_contract_and_send.py -v

# Подпись контракта работником
pytest tests/test_e2e_scenario/test_3_sign_by_worker.py -v

# Запуск всех E2E тестов
pytest tests/test_e2e_scenario/ -v

# Запуск всех UI тестов
pytest -m ui -v
```

### 📊 Генерация отчетов Allure
```bash
# Запуск тестов с генерацией Allure отчета
pytest tests/test_e2e_scenario/ --alluredir=allure-results -v

# Просмотр отчета
allure serve allure-results
```

## Примеры использования API клиента

### Авторизация через OTP
```python
from api.api_client import APIClient

# Создаем клиента
client = APIClient()

# Отправляем OTP на email
client.send_otp("user@example.com")

# Вводим OTP код из email и получаем токены
auth_data = client.verify_otp("user@example.com", "123456")
print(f"Токен: {auth_data['access']}")
```

### Работа с контрактами
```python
# Получаем список компаний
companies = client.get_companies()
company_id = companies[0]['id']

# Создаем контракт
contract_data = {
    "title": "Разработка сайта",
    "amount": "100000.00",
    "currency": "RUB"
}
contract = client.create_contract_for_company(company_id, contract_data)

# Подписываем контракт через OTP
client.sign_contract_otp(contract['id'])
client.sign_contract_otp_verify(contract['id'], "654321")
```

### Использование в тестах
```python
def test_companies_list(api_client):
    """Тест получения списка компаний"""
    companies = api_client.get_companies()
    assert isinstance(companies, list)

def test_otp_auth_mocked():
    """Тест OTP авторизации с моками"""
    from unittest.mock import Mock, patch
    
    client = APIClient()
    with patch.object(client.session, 'request') as mock:
        mock.return_value = Mock(status_code=200, json=lambda: {"status": "sent"})
        result = client.send_otp("test@example.com")
        assert result["status"] == "sent"
```

## CI/CD Integration

Проект настроен для работы в GitHub Actions:

```yaml
# .github/workflows/tests.yml
- name: Run API Tests
  run: |
    python -m pytest tests/test_api_basic.py -v --tb=short
```

### Результаты тестов в Telegram
CI автоматически отправляет результаты в Telegram:
- ✅ Общая статистика тестов
- 🌐 Результаты API тестов 
- 🖥️ Результаты UI тестов
- 📊 Детальная информация об ошибках

## Типы тестов

- **API тесты** (`-m api`) - Тестирование REST API без UI (временно отключены)
- **UI тесты** (`-m ui`) - Тестирование пользовательского интерфейса
- **E2E тесты** - Полные пользовательские сценарии от начала до конца
- **Smoke тесты** (`-m smoke`) - Базовая проверка функциональности
- **Regression тесты** (`-m regression`) - Регрессионное тестирование

## Улучшения для стабильности в CI

### 🛠️ Новые методы в BasePage для надежного клика

Проект включает улучшенные методы для работы с элементами, особенно важные для CI окружения:

```python
# JavaScript клик для обхода перекрывающих элементов
base_page.js_click(locator)

# Умный клик с несколькими попытками
base_page.smart_click(
    primary_locator=(By.XPATH, "//button[text()='Primary']"),
    alternative_locator=(By.XPATH, "//div[text()='Alternative']")
)

# Проверка видимости элемента с ожиданием
base_page.check_element_visible(locator, timeout=30)
```

### 🎯 Специальные методы для проблемных элементов

```python
# Для кнопки подписания контракта (решает TimeoutException)
main_page.click_worker_sign_contract()

# Для клика по контракту в таблице (решает ElementClickInterceptedException)
contract_page.click_contract_by_email(email)
```

### 🔧 Автоматическое управление браузером

- **Автоопределение ChromeDriver** через `webdriver-manager`
- **Динамический порт отладки** для параллельного запуска
- **Улучшенная очистка** браузера после тестов
- **Стабильное закрытие вкладок** с подробным логированием

### 📊 Подробное логирование

Все методы включают детальное логирование для отладки:
- ✅ Успешные операции
- ❌ Ошибки с контекстом  
- 🔄 Попытки fallback методов
- 📸 Автоматические скриншоты при ошибках

## Документация

- 📚 **[API Examples](docs/api_examples.md)** - Подробные примеры использования всех методов API
- 🔗 **[Swagger Documentation](https://api.example-payroll.dev/api/swagger/)** - Официальная документация API
- ⚙️ **[Configuration](config/config.py)** - Настройки проекта

## Работа с базой данных

### 🗄️ PostgreSQL с SSH туннелем

Проект включает полнофункциональную работу с PostgreSQL через SSH туннель:

```python
from util.db.db_query import DBQuery

# Создание подключения с автоматическим SSH туннелем
db = DBQuery()

# Выполнение запросов
user_id = db.get_single_string_column_from_query(
    "SELECT id FROM auth_user WHERE email = %s", 
    ("user@example.com",)
)
```

### 🧹 Автоматическая очистка данных

Фикстура `clean_db_after_session` обеспечивает каскадное удаление тестовых данных:

- ✅ **Правильный порядок удаления** с учетом внешних ключей
- ✅ **Каскадное удаление** связанных записей
- ✅ **Безопасная очистка** без нарушения целостности БД

Поддерживаемые таблицы для очистки:
- `contracts_receiptsignature` → `contracts_receipt` → `contracts_contractsignature` → `contracts_contract`
- `user_profile`, `auth_user` и связанные таблицы

### 🔧 Утилиты базы данных

```python
from util.db.db_queries import DBQueries

# Получение OTP кодов для подписания
manager_otp = db.get_single_string_column_from_query(
    DBQueries.get_manager_signature_otp_by_contract_id(), 
    (contract_id,)
)

# Обновление статуса KYC
db.execute_query(
    DBQueries.update_user_kyc_status(), 
    ("APPROVED", user_id)
)

# Каскадное удаление пользователя
db.delete_user_cascade_by_email("test@example.com")
```

## Особенности API example-payroll.dev

1. **OTP Авторизация** - Вместо стандартного логин/пароль
2. **JWT Токены** - Access и Refresh токены для авторизации
3. **ID-based операции** - Многие методы требуют ID (например, профиль)
4. **Подписание через OTP** - Контракты и акты подписываются через OTP
5. **Методы вывода** - Система управления способами вывода средств
6. **PostgreSQL интеграция** - Прямая работа с базой для тестовых данных

## Примечания по миграции

Если вы обновляете существующий код:

1. **Метод `login()`** теперь только отправляет OTP - используйте `verify_otp()` для получения токенов
2. **Метод `get_profile()`** требует `user_id` параметр
3. **Методы пользователей** (`get_users`, `create_user` и т.д.) удалены - их нет в реальном API
4. **Методы платежей** удалены - вместо них используются акты (receipts)
5. **Новые методы контрактов** для подписания через OTP

## Полезные ссылки

- [Swagger API Documentation](https://api.example-payroll.dev/api/swagger/)
- [GitHub Repository](https://github.com/your-repo/pay-roll_autotests)

## 🔄 Последние обновления (Сентябрь 2025)

### ✨ Новые возможности:
- 🛠️ **Улучшенные методы клика** - `js_click()`, `smart_click()` для стабильности в CI
- 🎭 **E2E тесты** - Полные пользовательские сценарии  
- 🗄️ **Каскадная очистка БД** - Исправлена фикстура `clean_db_after_session`
- 🔧 **Автоматическое управление браузером** - ChromeDriver через webdriver-manager
- 📱 **Стабильное закрытие вкладок** - Улучшенная функция `close_all_tabs_except_first`

### 🐛 Исправленные ошибки:
- ❌ **ElementClickInterceptedException** в CI окружении
- ❌ **TimeoutException** для кнопки подписания контракта
- ❌ **ForeignKeyViolation** при очистке БД
- ❌ **ChromeDriver версии** - автоматическое обновление

### 🏗️ Техническая архитектура:
- **Python 3.10+** с виртуальным окружением
- **Selenium 4.24+** с Selenium-Wire для перехвата сетевых запросов
- **PostgreSQL** с SSH туннелем для тестовых данных
- **Allure Reports** для детальной отчетности
- **Pytest** с кастомными фикстурами и маркерами

---

**Автор:** Команда разработки pay-roll  
**Дата обновления:** Сентябрь 2025  
**Версия тестов:** 2.0.0  
**Версия API:** 1.0.0

 