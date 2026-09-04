import pyotp
import allure
from typing import Optional


class OTPHelper:
    @staticmethod
    @allure.step("Генерация OTP кода из секретного ключа")
    def generate_otp_from_secret(otp_secret: str, interval: int = 300) -> str:
        """
        Генерирует актуальный OTP код из секретного ключа
        
        Args:
            otp_secret: Секретный ключ в формате base32 (например: AIG6QLDGGRD674MHE2BAJO4JZTUOZYQY)
            interval: Интервал в секундах (по умолчанию 300 = 5 минут)
        
        Returns:
            str: OTP код в формате XXX-XXX (например: 307-870)
        """
        try:
            # Создаем TOTP объект с тем же интервалом, что используется в бэкенде
            totp = pyotp.TOTP(otp_secret, interval=interval)
            
            # Генерируем текущий OTP код
            otp_code = totp.now()
            
            # Форматируем код в вид XXX-XXX
            formatted_code = f"{otp_code[:3]}-{otp_code[3:]}"
            
            print(f"Сгенерирован OTP код: {formatted_code} из ключа: {otp_secret[:8]}...")
            return formatted_code
            
        except Exception as e:
            print(f"Ошибка при генерации OTP кода: {e}")
            raise
    
    @staticmethod
    @allure.step("Проверка валидности OTP кода")
    def verify_otp(otp_secret: str, otp_code: str, interval: int = 300) -> bool:
        """
        Проверяет валидность OTP кода
        
        Args:
            otp_secret: Секретный ключ
            otp_code: OTP код для проверки (в формате XXX-XXX или XXXXXX)
            interval: Интервал в секундах
        
        Returns:
            bool: True если код валидный
        """
        try:
            # Убираем дефис из кода если он есть
            clean_code = otp_code.replace("-", "")
            
            totp = pyotp.TOTP(otp_secret, interval=interval)
            is_valid = totp.verify(clean_code)
            
            print(f"Проверка OTP кода {otp_code}: {'✓ Валидный' if is_valid else '✗ Невалидный'}")
            return is_valid
            
        except Exception as e:
            print(f"Ошибка при проверке OTP кода: {e}")
            return False
    
    @staticmethod
    @allure.step("Получение следующего OTP кода")
    def get_next_otp(otp_secret: str, interval: int = 300) -> str:
        """
        Получает следующий OTP код (для следующего временного окна)
        
        Args:
            otp_secret: Секретный ключ
            interval: Интервал в секундах
        
        Returns:
            str: Следующий OTP код в формате XXX-XXX
        """
        try:
            import time
            
            totp = pyotp.TOTP(otp_secret, interval=interval)
            
            # Получаем код для следующего временного окна
            current_time = int(time.time())
            next_window_time = current_time + interval
            next_otp = totp.at(next_window_time)
            
            formatted_code = f"{next_otp[:3]}-{next_otp[3:]}"
            print(f"Следующий OTP код: {formatted_code}")
            return formatted_code
            
        except Exception as e:
            print(f"Ошибка при получении следующего OTP кода: {e}")
            raise
    
    @staticmethod
    def format_otp_code(otp_code: str) -> str:
        """
        Форматирует OTP код в вид XXX-XXX
        
        Args:
            otp_code: OTP код (6 цифр)
        
        Returns:
            str: Отформатированный код XXX-XXX
        """
        clean_code = otp_code.replace("-", "").replace(" ", "")
        if len(clean_code) == 6:
            return f"{clean_code[:3]}-{clean_code[3:]}"
        return clean_code
    
    @staticmethod
    def clean_otp_code(otp_code: str) -> str:
        """
        Очищает OTP код от форматирования
        
        Args:
            otp_code: OTP код (может быть XXX-XXX или XXXXXX)
        
        Returns:
            str: Очищенный код из 6 цифр
        """
        return otp_code.replace("-", "").replace(" ", "")


# Функции для удобства использования
def generate_otp(otp_secret: str) -> str:
    """Быстрая генерация OTP кода"""
    return OTPHelper.generate_otp_from_secret(otp_secret)


def verify_otp(otp_secret: str, otp_code: str) -> bool:
    """Быстрая проверка OTP кода"""
    return OTPHelper.verify_otp(otp_secret, otp_code) 