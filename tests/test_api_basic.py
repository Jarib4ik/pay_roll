"""
Базовые тесты для API клиента example-payroll.dev
"""
import pytest
from unittest.mock import Mock, patch
import requests
from api.api_client import APIClient


class TestAPIClient:

    def test_api_client_initialization(self):
        """Тест инициализации API клиента"""
        # Тест с базовыми параметрами
        client = APIClient()
        assert client.base_url == "https://api.example-payroll.dev"
        assert client.token is None
        
        # Тест с кастомными параметрами
        client = APIClient(base_url="https://test.api.com", token="test_token")
        assert client.base_url == "https://test.api.com"
        assert client.token == "test_token"
        assert client.session.headers["Authorization"] == "Bearer test_token"

    def test_url_building(self):
        """Тест построения URL"""
        client = APIClient(base_url="https://api.test.com")
        
        # Проверяем внутренний метод через мок
        with patch.object(client.session, 'request') as mock_request:
            mock_request.return_value = Mock(status_code=200, json=lambda: {})
            
            client._make_request("GET", "/api/v1/test/")
            
            # Проверяем что URL построен правильно
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[1] == "https://api.test.com/api/v1/test/"

    def test_network_error_handling(self):
        """Тест обработки сетевых ошибок"""
        client = APIClient()
        
        with patch.object(client.session, 'request', side_effect=requests.ConnectionError("Network error")):
            with pytest.raises(requests.ConnectionError):
                client._make_request("GET", "/api/v1/test/")

    def test_request_headers(self):
        """Тест заголовков запроса"""
        client = APIClient(token="test_token_123")
        
        assert "Content-Type" in client.session.headers
        assert "Accept" in client.session.headers
        assert "Authorization" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["Authorization"] == "Bearer test_token_123"

    def test_api_methods_exist(self):
        """Тест наличия всех методов API"""
        client = APIClient()
        
        # Проверяем основные методы авторизации
        assert hasattr(client, 'send_otp')
        assert hasattr(client, 'verify_otp')
        assert hasattr(client, 'refresh_token')
        assert hasattr(client, 'logout')
        
        # Проверяем методы профиля
        assert hasattr(client, 'get_profile')
        assert hasattr(client, 'update_profile')
        assert hasattr(client, 'accept_terms_and_policy')
        
        # Проверяем методы компаний
        assert hasattr(client, 'get_companies')
        assert hasattr(client, 'get_company_by_id')
        assert hasattr(client, 'create_contract_for_company')
        
        # Проверяем методы контрактов
        assert hasattr(client, 'get_contracts')
        assert hasattr(client, 'get_contract_by_id')
        assert hasattr(client, 'sign_contract_otp')
        assert hasattr(client, 'sign_contract_otp_verify')
        
        # Проверяем методы актов
        assert hasattr(client, 'get_receipts')
        assert hasattr(client, 'sign_receipt_otp')
        assert hasattr(client, 'sign_receipt_otp_verify')
        
        # Проверяем служебные методы
        assert hasattr(client, 'get_countries')
        assert hasattr(client, 'get_withdraw_methods')
        
        # Проверяем legacy методы
        assert hasattr(client, 'login')  # для совместимости
        assert hasattr(client, 'partial_update_profile')  # для совместимости

    def test_send_otp_mocked(self):
        """Тест отправки OTP кода"""
        client = APIClient()
        
        with patch.object(client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success", "message": "OTP sent"}
            mock_response.text = '{"status": "success"}'
            mock_request.return_value = mock_response
            
            result = client.send_otp("test@example.com")
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with(
                "POST",
                "https://api.example-payroll.dev/api/v1/send-otp/",
                json={"email": "test@example.com"}
            )

    def test_verify_otp_mocked(self):
        """Тест проверки OTP кода"""
        client = APIClient()
        
        with patch.object(client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access": "access_token_123",
                "refresh": "refresh_token_456"
            }
            mock_request.return_value = mock_response
            
            result = client.verify_otp("test@example.com", "123456")
            
            assert result["access"] == "access_token_123"
            assert result["refresh"] == "refresh_token_456"
            # Проверяем что токен обновился в клиенте
            assert client.token == "access_token_123"
            assert client.session.headers["Authorization"] == "Bearer access_token_123"

    def test_http_error_handling_mocked(self):
        """Тест обработки HTTP ошибок"""
        client = APIClient()
        
        with patch.object(client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_request.return_value = mock_response
            
            with pytest.raises(requests.HTTPError):
                client.get_companies()

    def test_token_refresh_mocked(self):
        """Тест обновления токена"""
        client = APIClient()
        
        with patch.object(client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"access": "new_access_token"}
            mock_request.return_value = mock_response
            
            result = client.refresh_token("refresh_token_456")
            
            assert result["access"] == "new_access_token"
            # Проверяем что новый токен установился
            assert client.token == "new_access_token"
            assert client.session.headers["Authorization"] == "Bearer new_access_token"

    def test_legacy_login_method(self):
        """Тест legacy метода login (должен вызывать send_otp)"""
        client = APIClient()
        
        with patch.object(client, 'send_otp') as mock_send_otp:
            mock_send_otp.return_value = {"status": "success"}
            
            result = client.login("test@example.com", "password")
            
            # Проверяем что вызывается send_otp вместо реальной авторизации
            mock_send_otp.assert_called_once_with("test@example.com")
            assert result["status"] == "success" 