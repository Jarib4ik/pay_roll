# API клиент example-payroll.dev - Документация и примеры

## Описание

Этот API клиент предназначен для работы с API системы Example Payroll System. API использует авторизацию через OTP (одноразовые пароли), JWT токены и предоставляет методы для работы с компаниями, контрактами, актами и платежными системами.

**⚠️ ВАЖНО:** API example-payroll.dev использует OTP авторизацию, а не стандартную логин/пароль систему!

## Базовое использование

### Создание клиента

```python
from api.api_client import APIClient

# Создание клиента без авторизации
client = APIClient()

# Создание клиента с кастомным URL и токеном
client = APIClient(
    base_url="https://api.example-payroll.dev",
    token="your_jwt_token_here"
)
```

### Переменные окружения

Вы можете использовать переменные окружения для настройки:

```bash
export API_BASE_URL="https://api.example-payroll.dev"
export API_TOKEN="your_jwt_token"
export TEST_API_TOKEN="test_token_for_mocks"
```

## Авторизация через OTP

### Шаг 1: Отправка OTP кода

```python
# Отправляем OTP код на email
result = client.send_otp("user@example.com")
print("OTP отправлен, проверьте почту")
```

### Шаг 2: Проверка OTP и получение токенов

```python
# Проверяем OTP код и получаем токены
auth_data = client.verify_otp("user@example.com", "123456")

print(f"Access token: {auth_data['access']}")
print(f"Refresh token: {auth_data['refresh']}")

# Токен автоматически установится в клиенте
print(f"Клиент авторизован: {client.token is not None}")
```

### Обновление токена

```python
# Обновляем access token с помощью refresh token
new_tokens = client.refresh_token("your_refresh_token")
print(f"Новый access token: {new_tokens['access']}")
```

### Выход из системы

```python
# Выходим из системы
client.logout("your_refresh_token")
print("Выход выполнен")
```

### Legacy метод login (для совместимости)

```python
# ВНИМАНИЕ: Этот метод только отправляет OTP!
result = client.login("user@example.com")  # пароль игнорируется
# Затем используйте verify_otp() для завершения авторизации
```

## Работа с профилем

### Получение данных профиля

```python
# Получаем профиль пользователя по ID
user_id = 123
profile = client.get_profile(user_id)

print(f"Email: {profile['email']}")
print(f"ID: {profile['id']}")
```

### Обновление профиля

```python
# Обновляем данные профиля
profile_data = {
    "first_name": "Новое имя",
    "last_name": "Новая фамилия",
    "phone": "+7-XXX-XXX-XX-XX"
}

updated_profile = client.update_profile(user_id, profile_data)
print("Профиль обновлен")
```

### Согласие с условиями

```python
# Принимаем Terms and Policy
result = client.accept_terms_and_policy(user_id)
print("Условия приняты")
```

## Работа с компаниями

### Получение списка компаний

```python
companies = client.get_companies()

for company in companies:
    print(f"Компания: {company['name']} (ID: {company['id']})")
```

### Получение компании по ID

```python
company_id = 1
company = client.get_company_by_id(company_id)
print(f"Компания: {company['name']}")
```

### Создание контракта для компании

```python
contract_data = {
    "title": "Контракт на разработку",
    "description": "Описание контракта",
    "amount": "100000.00",
    "currency": "RUB"
}

contract = client.create_contract_for_company(company_id, contract_data)
print(f"Контракт создан: {contract['id']}")
```

## Работа с контрактами

### Получение списка контрактов

```python
contracts = client.get_contracts()

for contract in contracts:
    print(f"Контракт: {contract['title']} (ID: {contract['id']})")
    print(f"Статус: {contract['status']}")
```

### Получение контракта по ID

```python
contract_id = 1
contract = client.get_contract_by_id(contract_id)
print(f"Контракт: {contract['title']}")
```

### Обновление контракта

```python
update_data = {
    "status": "active",
    "start_date": "2024-01-01T00:00:00Z"
}

updated_contract = client.update_contract(contract_id, update_data)
print("Контракт обновлен")
```

### Подписание контракта через OTP

```python
# Шаг 1: Запрашиваем отправку OTP для подписания
otp_result = client.sign_contract_otp(contract_id)
print("OTP для подписания отправлен")

# Шаг 2: Подтверждаем подписание с помощью OTP
sign_result = client.sign_contract_otp_verify(contract_id, "123456")
print("Контракт подписан")
```

### Дополнительные методы контрактов

```python
# Получение ссылки на документ
doc_link = client.get_contract_document_link(contract_id)
print(f"Ссылка на документ: {doc_link}")

# Получение примера шаблона
template_example = client.get_contract_template_example(contract_id)

# Добавление метода вывода к контракту
withdraw_data = {
    "method": "bank_card",
    "details": {"card_number": "4111111111111111"}
}
client.add_withdraw_method_to_contract(contract_id, withdraw_data)
```

## Работа с шаблонами контрактов

```python
# Получение списка шаблонов
templates = client.get_contract_templates()

# Создание нового шаблона
template_data = {
    "name": "Шаблон для IT услуг",
    "content": "Текст шаблона..."
}
new_template = client.create_contract_template(template_data)

# Добавление полей к шаблону
fields_data = {
    "fields": [
        {"name": "client_name", "type": "text"},
        {"name": "amount", "type": "number"}
    ]
}
client.add_fields_to_template(new_template['id'], fields_data)
```

## Работа с актами (Receipts)

### Получение списка актов

```python
receipts = client.get_receipts()

for receipt in receipts:
    print(f"Акт: {receipt['id']} - {receipt['status']}")
```

### Подписание акта через OTP

```python
receipt_id = 1
user_withdraw_method_id = 5

# Шаг 1: Запрашиваем OTP для подписания акта
client.sign_receipt_otp(receipt_id)
print("OTP для подписания акта отправлен")

# Шаг 2: Подписываем акт с OTP
result = client.sign_receipt_otp_verify(
    receipt_id, 
    "123456", 
    user_withdraw_method_id
)
print("Акт подписан")
```

### Получение приложения к акту

```python
exhibit = client.get_receipt_exhibit(receipt_id)
print(f"Приложение к акту: {exhibit}")
```

## Работа с методами вывода

```python
# Получение списка доступных методов вывода
methods = client.get_withdraw_methods()
for method in methods:
    print(f"Метод: {method['name']} (ID: {method['id']})")

# Добавление метода вывода пользователя
method_data = {
    "card_number": "4111111111111111",
    "cardholder_name": "IVAN IVANOV"
}
user_method = client.add_user_withdraw_method(method_id, method_data)

# Получение методов вывода пользователя
user_methods = client.get_user_withdraw_methods()
```

## Служебные методы

```python
# Получение списка стран
countries = client.get_countries()
for country in countries:
    print(f"{country['name']} ({country['code']})")

# Получение access token для SumSub (KYC)
sumsub_token = client.get_sumsub_access_token()
print(f"SumSub token: {sumsub_token}")
```

## Административные методы (для менеджеров)

```python
# Получение списка контрактов (для менеджеров)
manager_contracts = client.manager_get_contracts()

# Получение списка актов (для менеджеров)
manager_receipts = client.manager_get_receipts()

# Отправка контракта (для менеджеров)
contract_data = {"contract_id": 123, "recipient": "user@example.com"}
client.manager_send_contract(contract_data)

# Обновление контракта (для менеджеров)
update_data = {"contract_id": 123, "status": "approved"}
client.manager_update_contract(update_data)
```

## Использование в тестах

### С фикстурами pytest

```python
def test_get_companies(api_client):
    """Тест получения списка компаний"""
    companies = api_client.get_companies()
    assert isinstance(companies, list)

def test_otp_auth(api_client):
    """Тест OTP авторизации"""
    # Отправляем OTP
    result = api_client.send_otp("test@example.com")
    assert "status" in result
    
    # В реальном тесте здесь нужен настоящий OTP код
    # auth_data = api_client.verify_otp("test@example.com", "123456")
    # assert "access" in auth_data
```

### С моками

```python
from unittest.mock import Mock, patch

def test_companies_mocked():
    """Тест с мокированием ответа API"""
    client = APIClient()
    
    with patch.object(client.session, 'request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Тест Компания"}
        ]
        mock_request.return_value = mock_response
        
        companies = client.get_companies()
        assert len(companies) == 1
        assert companies[0]["name"] == "Тест Компания"
```

## Обработка ошибок

```python
import requests

try:
    companies = client.get_companies()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Ошибка авторизации - токен недействителен")
        # Попробуйте обновить токен или заново авторизоваться
    elif e.response.status_code == 404:
        print("Эндпоинт не найден")
    else:
        print(f"HTTP ошибка: {e.response.status_code}")
except requests.ConnectionError:
    print("Ошибка соединения с API")
```

## Логирование

Клиент автоматически логирует все запросы:

```python
import logging

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Теперь все API запросы будут логироваться
client = APIClient()
companies = client.get_companies()
```

## Валидация подписи контракта

```python
# Валидация подписи контракта
with open("contract_signature.pdf", "rb") as f:
    file_data = f.read()

validation_result = client.validate_contract_signature(
    contract_id=123,
    file_data=file_data
)
print(f"Результат валидации: {validation_result}")
```

## Кастомные запросы

Для запросов, не покрытых основными методами:

```python
# Выполнение кастомного запроса
response = APIClient.custom_request(
    method="GET",
    url="https://api.example-payroll.dev/api/v1/custom-endpoint/",
    headers={"Authorization": "Bearer your_token"}
)
print(response.json())
```

## Примеры полного workflow

### Полный цикл работы с контрактом

```python
# 1. Авторизация
client = APIClient()
client.send_otp("user@example.com")
# Пользователь получает OTP по email
auth_data = client.verify_otp("user@example.com", "123456")

# 2. Получение информации о компаниях
companies = client.get_companies()
company_id = companies[0]['id']

# 3. Создание контракта
contract_data = {
    "title": "Разработка сайта",
    "amount": "150000.00",
    "currency": "RUB"
}
contract = client.create_contract_for_company(company_id, contract_data)
contract_id = contract['id']

# 4. Подписание контракта
client.sign_contract_otp(contract_id)
# Пользователь получает OTP для подписания
client.sign_contract_otp_verify(contract_id, "654321")

# 5. Работа с актами
receipts = client.get_receipts()
if receipts:
    receipt_id = receipts[0]['id']
    client.sign_receipt_otp(receipt_id)
    # Подписание акта с методом вывода
    client.sign_receipt_otp_verify(receipt_id, "789012", user_withdraw_method_id=1)

print("Полный цикл завершен!")
```

Этот API клиент предоставляет полный набор методов для работы с системой Example Payroll System, включая авторизацию через OTP, управление контрактами, актами и платежными методами. 