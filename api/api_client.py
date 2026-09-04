import requests
from requests import Response
import logging
import json
from typing import Dict, Optional, Any
import os

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str = None, token: str = None):
        """
        Инициализация API клиента для example-payroll.dev
        
        Args:
            base_url: Базовый URL API (по умолчанию из конфигурации)
            token: JWT токен для авторизации
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "https://api.example-payroll.dev")
        self.token = token or os.getenv("API_TOKEN")
        self.session = requests.Session()
        
        # Устанавливаем базовые заголовки
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Добавляем токен авторизации если есть
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Response:
        """
        Выполняет HTTP запрос к API
        
        Args:
            method: HTTP метод (GET, POST, PUT, PATCH, DELETE)
            endpoint: Эндпоинт API (без базового URL)
            **kwargs: Дополнительные параметры для requests
        
        Returns:
            Response объект
        """
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"🌐 {method} {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            logger.info(f"📊 Статус: {response.status_code}")
            
            # Логируем ответ для отладки
            if response.status_code >= 400:
                logger.error(f"❌ Ошибка API: {response.status_code} - {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка соединения: {e}")
            raise

    # === МЕТОДЫ АВТОРИЗАЦИИ (OTP) ===
    
    def send_otp(self, email: str) -> Dict[str, Any]:
        """
        Отправка OTP кода на email
        
        Args:
            email: Email пользователя
        
        Returns:
            Результат отправки OTP
        """
        data = {"email": email}
        
        response = self._make_request("POST", "/api/v1/send-otp/", json=data)
        
        if response.status_code == 200:
            return response.json() if response.text else {"status": "success"}
        else:
            response.raise_for_status()

    def verify_otp(self, email: str, otp: str) -> Dict[str, Any]:
        """
        Проверка OTP кода и получение токенов
        
        Args:
            email: Email пользователя
            otp: OTP код из email
        
        Returns:
            Данные ответа с токенами
        """
        data = {
            "email": email,
            "otp": otp
        }
        
        response = self._make_request("POST", "/api/v1/verify-otp/", json=data)
        
        if response.status_code == 200:
            auth_data = response.json()
            # Обновляем токен в сессии
            if "access" in auth_data:
                self.token = auth_data["access"]
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
            return auth_data
        else:
            response.raise_for_status()

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновление токена доступа
        
        Args:
            refresh_token: Токен обновления
        
        Returns:
            Новый токен доступа
        """
        data = {"refresh": refresh_token}
        response = self._make_request("POST", "/api/v1/token/refresh/", json=data)
        
        if response.status_code == 200:
            token_data = response.json()
            if "access" in token_data:
                self.token = token_data["access"]
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
            return token_data
        else:
            response.raise_for_status()

    def logout(self, refresh_token: str = None) -> bool:
        """
        Выход из системы
        
        Args:
            refresh_token: Токен обновления для отзыва (опционально)
        
        Returns:
            True если успешно
        """
        data = {}
        if refresh_token:
            data["refresh"] = refresh_token
            
        response = self._make_request("POST", "/api/v1/logout/", json=data)
        
        if response.status_code in [200, 204]:
            # Удаляем токен из сессии
            self.token = None
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            return True
        else:
            response.raise_for_status()

    # === МЕТОДЫ ПРОФИЛЯ ===
    
    def get_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Получение данных профиля пользователя по ID
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Данные профиля пользователя
        """
        response = self._make_request("GET", f"/api/v1/profile/{user_id}/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновление профиля пользователя
        
        Args:
            user_id: ID пользователя
            profile_data: Данные для обновления профиля
        
        Returns:
            Обновленные данные профиля
        """
        response = self._make_request("PATCH", f"/api/v1/profile/{user_id}/", json=profile_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def accept_terms_and_policy(self, user_id: int) -> Dict[str, Any]:
        """
        Согласие с Terms and Policy
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Результат согласия
        """
        response = self._make_request("POST", f"/api/v1/profile/{user_id}/accept_terms_and_policy/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === МЕТОДЫ КОМПАНИЙ ===
    
    def get_companies(self) -> list[Dict[str, Any]]:
        """
        Получение списка компаний текущего пользователя
        
        Returns:
            Список компаний
        """
        response = self._make_request("GET", "/api/v1/companies/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_company_by_id(self, company_id: int) -> Dict[str, Any]:
        """
        Получение компании по ID
        
        Args:
            company_id: ID компании
        
        Returns:
            Данные компании
        """
        response = self._make_request("GET", f"/api/v1/companies/{company_id}/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def create_contract_for_company(self, company_id: int, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание контракта для компании
        
        Args:
            company_id: ID компании
            contract_data: Данные контракта
        
        Returns:
            Данные созданного контракта
        """
        response = self._make_request("POST", f"/api/v1/companies/{company_id}/contract/", json=contract_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === МЕТОДЫ КОНТРАКТОВ ===
    
    def get_contracts(self) -> list[Dict[str, Any]]:
        """
        Получение списка контрактов текущего пользователя
        
        Returns:
            Список контрактов
        """
        response = self._make_request("GET", "/api/v1/contracts/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_contract_by_id(self, contract_id: int) -> Dict[str, Any]:
        """
        Получение контракта по ID
        
        Args:
            contract_id: ID контракта
        
        Returns:
            Данные контракта
        """
        response = self._make_request("GET", f"/api/v1/contracts/{contract_id}/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def update_contract(self, contract_id: int, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновление контракта
        
        Args:
            contract_id: ID контракта
            contract_data: Новые данные контракта
        
        Returns:
            Обновленные данные контракта
        """
        response = self._make_request("PATCH", f"/api/v1/contracts/{contract_id}/", json=contract_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def add_withdraw_method_to_contract(self, contract_id: int, withdraw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавление метода вывода к контракту
        
        Args:
            contract_id: ID контракта
            withdraw_data: Данные метода вывода
        
        Returns:
            Результат добавления
        """
        response = self._make_request("POST", f"/api/v1/contracts/{contract_id}/add_withdraw_method/", json=withdraw_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_contract_document_link(self, contract_id: int) -> Dict[str, Any]:
        """
        Получение ссылки на документ контракта
        
        Args:
            contract_id: ID контракта
        
        Returns:
            Ссылка на документ
        """
        response = self._make_request("GET", f"/api/v1/contracts/{contract_id}/get_document_link/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_contract_template_example(self, contract_id: int) -> Dict[str, Any]:
        """
        Получение примера шаблона контракта
        
        Args:
            contract_id: ID контракта
        
        Returns:
            Пример шаблона
        """
        response = self._make_request("GET", f"/api/v1/contracts/{contract_id}/get_template_example/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def sign_contract_otp(self, contract_id: int) -> Dict[str, Any]:
        """
        Подписание контракта - отправка OTP кода
        
        Args:
            contract_id: ID контракта
        
        Returns:
            Результат отправки OTP
        """
        response = self._make_request("POST", f"/api/v1/contracts/{contract_id}/sign_otp/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def sign_contract_otp_verify(self, contract_id: int, otp: str) -> Dict[str, Any]:
        """
        Подписание контракта - проверка OTP кода
        
        Args:
            contract_id: ID контракта
            otp: OTP код
        
        Returns:
            Результат подписания
        """
        data = {"otp": otp}
        response = self._make_request("POST", f"/api/v1/contracts/{contract_id}/sign_otp_verify/", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def validate_contract_signature(self, contract_id: int, file_data: Any) -> Dict[str, Any]:
        """
        Валидация подписи контракта
        
        Args:
            contract_id: ID контракта
            file_data: Файл для валидации
        
        Returns:
            Результат валидации
        """
        data = {
            "contract_id": contract_id,
            "file": file_data
        }
        response = self._make_request("POST", "/api/v1/contracts/validate_signature/", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === МЕТОДЫ ШАБЛОНОВ КОНТРАКТОВ ===
    
    def get_contract_templates(self) -> list[Dict[str, Any]]:
        """
        Получение списка шаблонов контрактов
        
        Returns:
            Список шаблонов контрактов
        """
        response = self._make_request("GET", "/api/v1/contract_templates/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def create_contract_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание шаблона контракта
        
        Args:
            template_data: Данные шаблона
        
        Returns:
            Данные созданного шаблона
        """
        response = self._make_request("POST", "/api/v1/contract_templates/", json=template_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def add_fields_to_template(self, template_id: int, fields_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавление полей к шаблону контракта
        
        Args:
            template_id: ID шаблона
            fields_data: Данные полей
        
        Returns:
            Результат добавления полей
        """
        response = self._make_request("POST", f"/api/v1/contract_templates/{template_id}/add_fields/", json=fields_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === МЕТОДЫ АКТОВ (RECEIPTS) ===
    
    def get_receipts(self) -> list[Dict[str, Any]]:
        """
        Получение списка актов
        
        Returns:
            Список актов
        """
        response = self._make_request("GET", "/api/v1/receipts/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_receipt_exhibit(self, receipt_id: int) -> Dict[str, Any]:
        """
        Получение приложения к акту
        
        Args:
            receipt_id: ID акта
        
        Returns:
            Данные приложения
        """
        response = self._make_request("GET", f"/api/v1/receipts/{receipt_id}/get_exhibit/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def sign_receipt_otp(self, receipt_id: int) -> Dict[str, Any]:
        """
        Подписание акта - отправка OTP кода
        
        Args:
            receipt_id: ID акта
        
        Returns:
            Результат отправки OTP
        """
        response = self._make_request("POST", f"/api/v1/receipts/{receipt_id}/sign_otp/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def sign_receipt_otp_verify(self, receipt_id: int, otp: str, user_withdraw_method_id: int) -> Dict[str, Any]:
        """
        Подписание акта - проверка OTP кода
        
        Args:
            receipt_id: ID акта
            otp: OTP код
            user_withdraw_method_id: ID метода вывода пользователя
        
        Returns:
            Результат подписания
        """
        data = {
            "otp": otp,
            "user_withdraw_method_id": user_withdraw_method_id
        }
        response = self._make_request("POST", f"/api/v1/receipts/{receipt_id}/sign_otp_verify/", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === МЕТОДЫ ВЫВОДА СРЕДСТВ ===
    
    def get_withdraw_methods(self) -> list[Dict[str, Any]]:
        """
        Получение списка методов вывода
        
        Returns:
            Список методов вывода
        """
        response = self._make_request("GET", "/api/v1/withdraw_methods/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def add_user_withdraw_method(self, method_id: int, method_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавление метода вывода пользователя
        
        Args:
            method_id: ID метода вывода
            method_data: Данные метода
        
        Returns:
            Данные добавленного метода
        """
        response = self._make_request("POST", f"/api/v1/withdraw_methods/{method_id}/add_user_withdraw_method/", json=method_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_user_withdraw_methods(self) -> list[Dict[str, Any]]:
        """
        Получение методов вывода пользователя
        
        Returns:
            Список методов вывода пользователя
        """
        response = self._make_request("GET", "/api/v1/withdraw_methods/user_withdraw_methods/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # === СЛУЖЕБНЫЕ МЕТОДЫ ===
    
    def get_countries(self) -> list[Dict[str, Any]]:
        """
        Получение списка стран
        
        Returns:
            Список стран
        """
        response = self._make_request("GET", "/api/v1/countries/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_sumsub_access_token(self) -> str:
        """
        Получение access token для SumSub
        
        Returns:
            Access token для SumSub
        """
        response = self._make_request("GET", "/api/v1/sumsub/access_token/")
        
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()

    # === АДМИНИСТРАТИВНЫЕ МЕТОДЫ ===
    
    def manager_get_contracts(self) -> list[Dict[str, Any]]:
        """
        Получение списка контрактов (для менеджеров)
        
        Returns:
            Список контрактов
        """
        response = self._make_request("GET", "/api/v1/manager/contracts/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def manager_get_receipts(self) -> list[Dict[str, Any]]:
        """
        Получение списка актов (для менеджеров)
        
        Returns:
            Список актов
        """
        response = self._make_request("GET", "/api/v1/manager/receipts/")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def manager_send_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка контракта (для менеджеров)
        
        Args:
            contract_data: Данные контракта
        
        Returns:
            Результат отправки
        """
        response = self._make_request("POST", "/api/v1/manager/send_contract/", json=contract_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def manager_update_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновление контракта (для менеджеров)
        
        Args:
            contract_data: Данные контракта
        
        Returns:
            Результат обновления
        """
        response = self._make_request("POST", "/api/v1/manager/update_contract/", json=contract_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @staticmethod
    def custom_request(method: str, url: str, **kwargs) -> Response:
        """
        Кастомный HTTP запрос (для обратной совместимости)
        
        Args:
            method: HTTP метод
            url: Полный URL
            **kwargs: Дополнительные параметры
        
        Returns:
            Response объект
        """
        return requests.request(method, url, **kwargs)

    # === МЕТОДЫ УДОБСТВА (LEGACY COMPATIBILITY) ===
    
    def login(self, email: str, password: str = None) -> Dict[str, Any]:
        """
        Упрощенный метод авторизации через OTP
        ВНИМАНИЕ: Этот метод только отправляет OTP!
        Используйте verify_otp() для завершения авторизации.
        
        Args:
            email: Email пользователя
            password: Игнорируется (для совместимости)
        
        Returns:
            Результат отправки OTP
        """
        logger.warning("⚠️ login() только отправляет OTP. Используйте verify_otp() для получения токенов.")
        return self.send_otp(email)

    def partial_update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Алиас для update_profile (для совместимости)
        
        Args:
            user_id: ID пользователя
            profile_data: Данные для обновления
        
        Returns:
            Обновленные данные профиля
        """
        return self.update_profile(user_id, profile_data)