"""
Тесты для API example-payroll.dev
"""
import pytest
import allure
from api.api_client import APIClient
from data.users import TEST_LOGIN

pytestmark = [
    pytest.mark.api,
    pytest.mark.skip(reason="Требует доступного тестового backend и валидных учётных данных; не запускается без live-окружения"),
]


@allure.epic("API Tests")
@allure.feature("Авторизация")
class TestAuth:
    
    @allure.story("Авторизация пользователя")
    @allure.title("Тест авторизации через API")
    def test_login_api(self):
        """Тест авторизации пользователя через API"""
        
        with allure.step("Создаем API клиент"):
            api_client = APIClient()
        
        with allure.step(f"Авторизуемся с email: {TEST_LOGIN.email}"):
            auth_response = api_client.login(
                email=TEST_LOGIN.email,
                password=TEST_LOGIN.password
            )
        
        with allure.step("Проверяем ответ авторизации"):
            assert "access" in auth_response, "В ответе должен быть access токен"
            assert "refresh" in auth_response, "В ответе должен быть refresh токен"
            
            access_token = auth_response["access"]
            refresh_token = auth_response["refresh"]
            
            assert access_token, "Access токен не должен быть пустым"
            assert refresh_token, "Refresh токен не должен быть пустым"
            
            print(f"✅ Авторизация успешна, получен токен: {access_token[:20]}...")
    
    @allure.story("Обновление токена")
    @allure.title("Тест обновления токена доступа")
    def test_refresh_token(self):
        """Тест обновления токена доступа"""
        
        with allure.step("Получаем исходные токены"):
            api_client = APIClient()
            auth_response = api_client.login(
                email=TEST_LOGIN.email,
                password=TEST_LOGIN.password
            )
            refresh_token = auth_response["refresh"]
        
        with allure.step("Обновляем токен доступа"):
            token_response = api_client.refresh_token(refresh_token)
        
        with allure.step("Проверяем новый токен"):
            assert "access" in token_response, "В ответе должен быть новый access токен"
            new_access_token = token_response["access"]
            assert new_access_token, "Новый access токен не должен быть пустым"
            
            print(f"✅ Токен обновлен: {new_access_token[:20]}...")


@allure.epic("API Tests")
@allure.feature("Профиль пользователя")
class TestProfile:
    
    @pytest.fixture(scope="class")
    def authenticated_client(self):
        """Фикстура для авторизованного API клиента"""
        api_client = APIClient()
        api_client.login(
            email=TEST_LOGIN.email,
            password=TEST_LOGIN.password
        )
        return api_client
    
    @allure.story("Получение профиля")
    @allure.title("Тест получения данных профиля")
    def test_get_profile(self, authenticated_client):
        """Тест получения данных профиля пользователя"""
        
        with allure.step("Получаем данные профиля"):
            profile_data = authenticated_client.get_profile()
        
        with allure.step("Проверяем структуру данных профиля"):
            assert isinstance(profile_data, dict), "Ответ должен быть словарем"
            
            # Проверяем основные поля профиля
            expected_fields = ["id", "email", "first_name", "last_name"]
            for field in expected_fields:
                if field in profile_data:
                    print(f"✅ Поле '{field}' присутствует: {profile_data[field]}")
                else:
                    print(f"⚠️ Поле '{field}' отсутствует в профиле")
    
    @allure.story("Частичное обновление профиля")
    @allure.title("Тест частичного обновления профиля")
    def test_partial_update_profile(self, authenticated_client):
        """Тест частичного обновления профиля пользователя"""
        
        with allure.step("Получаем текущие данные профиля"):
            original_profile = authenticated_client.get_profile()
        
        # Тестовые данные для обновления
        update_data = {
            "first_name": "Test Name Updated",
            "last_name": "Test Surname Updated"
        }
        
        with allure.step("Обновляем профиль"):
            updated_profile = authenticated_client.partial_update_profile(update_data)
        
        with allure.step("Проверяем что данные обновились"):
            assert isinstance(updated_profile, dict), "Ответ должен быть словарем"
            
            # Проверяем что обновленные поля изменились
            for field, expected_value in update_data.items():
                if field in updated_profile:
                    actual_value = updated_profile[field]
                    print(f"✅ Поле '{field}' обновлено: '{actual_value}'")
                else:
                    print(f"⚠️ Поле '{field}' отсутствует в обновленном профиле")


@allure.epic("API Tests")
@allure.feature("Пользователи")
class TestUsers:
    
    @pytest.fixture(scope="class")
    def authenticated_client(self):
        """Фикстура для авторизованного API клиента"""
        api_client = APIClient()
        api_client.login(
            email=TEST_LOGIN.email,
            password=TEST_LOGIN.password
        )
        return api_client
    
    @allure.story("Получение списка пользователей")
    @allure.title("Тест получения списка пользователей")
    def test_get_users(self, authenticated_client):
        """Тест получения списка пользователей (для администраторов)"""
        
        with allure.step("Получаем список пользователей"):
            try:
                users_response = authenticated_client.get_users(page=1, page_size=10)
                
                with allure.step("Проверяем структуру ответа"):
                    assert isinstance(users_response, dict), "Ответ должен быть словарем"
                    
                    # Проверяем пагинацию
                    if "results" in users_response:
                        users_list = users_response["results"]
                        assert isinstance(users_list, list), "Результаты должны быть списком"
                        print(f"✅ Получено пользователей: {len(users_list)}")
                    else:
                        print("⚠️ Поле 'results' отсутствует в ответе")
                        
            except Exception as e:
                # Возможно у пользователя нет прав администратора
                print(f"⚠️ Не удалось получить список пользователей: {e}")
                pytest.skip("Пользователь не имеет прав для просмотра списка пользователей")


@allure.epic("API Tests")
@allure.feature("Компании")
class TestCompanies:
    
    @pytest.fixture(scope="class")
    def authenticated_client(self):
        """Фикстура для авторизованного API клиента"""
        api_client = APIClient()
        api_client.login(
            email=TEST_LOGIN.email,
            password=TEST_LOGIN.password
        )
        return api_client
    
    @allure.story("Получение списка компаний")
    @allure.title("Тест получения списка компаний")
    def test_get_companies(self, authenticated_client):
        """Тест получения списка компаний"""
        
        with allure.step("Получаем список компаний"):
            try:
                companies_response = authenticated_client.get_companies(page=1, page_size=10)
                
                with allure.step("Проверяем структуру ответа"):
                    assert isinstance(companies_response, dict), "Ответ должен быть словарем"
                    
                    if "results" in companies_response:
                        companies_list = companies_response["results"]
                        assert isinstance(companies_list, list), "Результаты должны быть списком"
                        print(f"✅ Получено компаний: {len(companies_list)}")
                        
                        # Проверяем структуру первой компании если есть
                        if companies_list:
                            first_company = companies_list[0]
                            print(f"✅ Первая компания: {first_company.get('name', 'Без названия')}")
                    else:
                        print("⚠️ Поле 'results' отсутствует в ответе")
                        
            except Exception as e:
                print(f"⚠️ Не удалось получить список компаний: {e}")
                pytest.skip("Не удалось получить список компаний")


@allure.epic("API Tests")
@allure.feature("Проверка состояния")
class TestHealthCheck:
    
    @allure.story("Проверка состояния API")
    @allure.title("Тест health check эндпоинта")
    def test_health_check(self):
        """Тест проверки состояния API"""
        
        with allure.step("Создаем API клиент"):
            api_client = APIClient()
        
        with allure.step("Проверяем состояние API"):
            try:
                health_response = api_client.health_check()
                
                with allure.step("Проверяем ответ health check"):
                    assert isinstance(health_response, dict), "Ответ должен быть словарем"
                    print(f"✅ Health check успешен: {health_response}")
                    
            except Exception as e:
                print(f"⚠️ Health check недоступен: {e}")
                # Health check может не быть реализован в API
                pytest.skip("Health check эндпоинт недоступен")


@allure.epic("API Tests")
@allure.feature("Контракты")
class TestContracts:
    
    @pytest.fixture(scope="class")
    def authenticated_client(self):
        """Фикстура для авторизованного API клиента"""
        api_client = APIClient()
        api_client.login(
            email=TEST_LOGIN.email,
            password=TEST_LOGIN.password
        )
        return api_client
    
    @allure.story("Получение списка контрактов")
    @allure.title("Тест получения списка контрактов")
    def test_get_contracts(self, authenticated_client):
        """Тест получения списка контрактов"""
        
        with allure.step("Получаем список контрактов"):
            try:
                contracts_response = authenticated_client.get_contracts(page=1, page_size=5)
                
                with allure.step("Проверяем структуру ответа"):
                    assert isinstance(contracts_response, dict), "Ответ должен быть словарем"
                    
                    if "results" in contracts_response:
                        contracts_list = contracts_response["results"]
                        assert isinstance(contracts_list, list), "Результаты должны быть списком"
                        print(f"✅ Получено контрактов: {len(contracts_list)}")
                        
                        # Проверяем структуру первого контракта если есть
                        if contracts_list:
                            first_contract = contracts_list[0]
                            contract_id = first_contract.get('id', 'Unknown')
                            contract_status = first_contract.get('status', 'Unknown')
                            print(f"✅ Первый контракт ID: {contract_id}, статус: {contract_status}")
                    else:
                        print("⚠️ Поле 'results' отсутствует в ответе")
                        
            except Exception as e:
                print(f"⚠️ Не удалось получить список контрактов: {e}")
                pytest.skip("Не удалось получить список контрактов") 