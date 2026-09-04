"""
Вспомогательные функции для автотестов example-payroll.dev
"""
import time
import random
import string
from datetime import datetime
from urllib.parse import urljoin


def generate_random_email(domain="example.com"):
    """Генерирует случайный email адрес"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@{domain}"


def generate_random_string(length=8):
    """Генерирует случайную строку указанной длины"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_phone():
    """Генерирует случайный номер телефона"""
    return f"+7{random.randint(9000000000, 9999999999)}"


def wait_for_condition(condition_func, timeout=30, poll_interval=1):
    """
    Ожидает выполнения условия в течение заданного времени
    
    Args:
        condition_func: Функция, которая должна вернуть True
        timeout: Максимальное время ожидания в секундах
        poll_interval: Интервал проверки в секундах
    
    Returns:
        bool: True если условие выполнилось, False если время истекло
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(poll_interval)
    return False


def api_url(base_url, endpoint=""):
    """
    Формирует полный URL для API запросов
    
    Args:
        base_url: Базовый URL
        endpoint: API endpoint
    
    Returns:
        str: Полный URL
    """
    if not base_url.endswith('/'):
        base_url += '/'
    
    # Для example-payroll.dev API может быть по адресу /api/
    api_base = urljoin(base_url, "api/")
    
    if endpoint:
        return urljoin(api_base, endpoint)
    return api_base


def format_timestamp():
    """Возвращает текущее время в формате для логов"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def take_screenshot_name(test_name, action):
    """
    Генерирует имя для скриншота
    
    Args:
        test_name: Название теста
        action: Действие
    
    Returns:
        str: Имя файла скриншота
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{test_name}_{action}_{timestamp}.png" 