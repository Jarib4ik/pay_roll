import psycopg2
from psycopg2 import Error
import psycopg2.extras
from typing import Tuple
import os


class PostgreSQLDatabaseManager:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        ssh_host: str = None,
        ssh_username: str = None,
        ssh_password: str = None,
        ssh_key_file: str = None,
        ssh_key_password: str = None,
        local_bind_port: int = 5432,
    ):
        """
        Инициализация соединения с базой данных PostgreSQL через SSH туннель.
        :param host: Хост базы данных.
        :param user: Пользователь базы данных.
        :param password: Пароль пользователя базы данных.
        :param database: Имя базы данных.
        :param ssh_host: SSH-хост для туннеля.
        :param ssh_username: SSH-пользователь.
        :param ssh_password: SSH-пароль (опционально).
        :param ssh_key_file: Путь к SSH-ключу (опционально).
        :param ssh_key_password: Пароль для SSH-ключа (опционально).
        :param local_bind_port: Локальный порт для привязки туннеля.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.tunnel = None

        # SSH параметры
        self.ssh_host = ssh_host or os.getenv("SSH_HOST")
        self.ssh_username = ssh_username or os.getenv("SSH_USER")
        self.ssh_password = ssh_password or os.getenv("SSH_PASSWORD")
        self.ssh_key_file = ssh_key_file or os.getenv("SSH_KEY_FILE")
        self.ssh_key_content = os.getenv("SSH_PRIVATE_KEY")  # Содержимое ключа из переменной
        self.ssh_key_password = ssh_key_password or os.getenv("SSH_KEY_PASSWORD")
        self.ssh_port = int(os.getenv("SSH_PORT", "22"))  # SSH порт, по умолчанию 22
        self.local_bind_port = local_bind_port
        self.temp_key_path = None  # Путь к временному файлу ключа

        # Если определен SSH-хост, значит нужен туннель
        self.use_ssh = bool(self.ssh_host)

    def connect(self):
        """Устанавливает соединение с базой данных PostgreSQL, опционально через SSH-туннель."""
        if self.connection is not None and not self.connection.closed:
            raise RuntimeError("Соединение уже установлено.")

        try:
            if self.use_ssh:
                print(f"Подключение через SSH: {self.ssh_host}")
                # Настраиваем SSH-туннель
                tunnel_params = {
                    "ssh_address_or_host": (self.ssh_host, self.ssh_port),
                    "ssh_username": self.ssh_username,
                    "remote_bind_address": (self.host, 5432),
                }

                try:
                    import sshtunnel

                    forwarder_args = (
                        sshtunnel.SSHTunnelForwarder.__init__.__code__.co_varnames
                    )
                    if "allow_agent" in forwarder_args:
                        tunnel_params["allow_agent"] = False
                    print(f"Доступные параметры sshtunnel: {forwarder_args}")
                except Exception as e:
                    print(f"Не удалось получить параметры sshtunnel: {e}")

                # Добавляем аутентификацию - приоритет: ключ из переменной, потом ключ из файла, потом пароль
                if self.ssh_key_content:
                    # Если есть содержимое ключа из переменной окружения
                    import tempfile
                    
                    print("🔑 Обрабатываем SSH ключ из переменной окружения...")
                    print(f"🔍 Длина ключа: {len(self.ssh_key_content)} символов")
                    
                    # Исправляем потенциальные проблемы с переносами строк в SSH ключе
                    # GitHub Actions иногда заменяет \n на \\n в secrets
                    ssh_key_fixed = self.ssh_key_content.replace('\\n', '\n')
                    if ssh_key_fixed != self.ssh_key_content:
                        print("🔧 Исправлены переносы строк в SSH ключе (\\n -> \n)")
                        self.ssh_key_content = ssh_key_fixed
                    
                    # Проверяем заголовки ключа
                    if "-----BEGIN" in self.ssh_key_content and "-----END" in self.ssh_key_content:
                        print("✅ SSH ключ содержит правильные заголовки")
                    else:
                        print("❌ SSH ключ НЕ содержит правильные заголовки!")
                    
                    # Создаем временный файл для ключа
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as key_file:
                        key_file.write(self.ssh_key_content)
                        self.temp_key_path = key_file.name
                    
                    # Устанавливаем правильные права доступа
                    os.chmod(self.temp_key_path, 0o600)
                    print(f"✅ Временный файл ключа создан: {self.temp_key_path}")
                    
                    # Проверяем что файл создался корректно
                    if os.path.exists(self.temp_key_path):
                        with open(self.temp_key_path, 'r') as f:
                            file_content = f.read()
                        print(f"🔍 Размер файла ключа: {len(file_content)} символов")
                        print(f"🔍 Содержимое совпадает: {file_content == self.ssh_key_content}")
                    
                    # Проверяем, защищен ли ключ паролем с помощью paramiko
                    try:
                        import paramiko
                        print("🔍 Проверяем SSH ключ с помощью paramiko...")
                        
                        try:
                            # Пробуем загрузить ключ как RSA
                            key = paramiko.RSAKey.from_private_key_file(self.temp_key_path)
                            print("✅ SSH ключ RSA загружен без пароля")
                        except paramiko.ssh_exception.PasswordRequiredException:
                            print("🔐 SSH ключ RSA требует пароль")
                            if not self.ssh_key_password:
                                print("❌ ОШИБКА: SSH ключ защищен паролем, но SSH_KEY_PASSWORD не установлен!")
                                print("🔧 Добавьте переменную SSH_KEY_PASSWORD в GitHub Secrets")
                                raise ValueError("SSH ключ требует пароль, но SSH_KEY_PASSWORD не предоставлен")
                        except Exception:
                            # Пробуем как ECDSA
                            try:
                                key = paramiko.ECDSAKey.from_private_key_file(self.temp_key_path)
                                print("✅ SSH ключ ECDSA загружен без пароля")
                            except paramiko.ssh_exception.PasswordRequiredException:
                                print("🔐 SSH ключ ECDSA требует пароль")
                                if not self.ssh_key_password:
                                    print("❌ ОШИБКА: SSH ключ защищен паролем, но SSH_KEY_PASSWORD не установлен!")
                                    raise ValueError("SSH ключ требует пароль, но SSH_KEY_PASSWORD не предоставлен")
                            except Exception:
                                # Пробуем как ED25519
                                try:
                                    key = paramiko.Ed25519Key.from_private_key_file(self.temp_key_path)
                                    print("✅ SSH ключ ED25519 загружен без пароля")
                                except paramiko.ssh_exception.PasswordRequiredException:
                                    print("🔐 SSH ключ ED25519 требует пароль")
                                    if not self.ssh_key_password:
                                        print("❌ ОШИБКА: SSH ключ защищен паролем, но SSH_KEY_PASSWORD не установлен!")
                                        raise ValueError("SSH ключ требует пароль, но SSH_KEY_PASSWORD не предоставлен")
                                except Exception as e:
                                    print(f"⚠️ Не удалось определить тип SSH ключа: {e}")
                                    print("🔄 Продолжаем с предположением что ключ работает...")
                        
                    except ImportError:
                        print("⚠️ paramiko не установлен, пропускаем проверку SSH ключа")
                    except Exception as e:
                        print(f"❌ Ошибка при проверке SSH ключа: {e}")
                        raise
                    
                    tunnel_params["ssh_pkey"] = self.temp_key_path
                    if self.ssh_key_password:
                        tunnel_params["ssh_private_key_password"] = self.ssh_key_password
                        print("🔐 Используем аутентификацию по ключу из переменной окружения с паролем.")
                    else:
                        print("🔓 Используем аутентификацию по ключу из переменной окружения без пароля.")
                elif self.ssh_key_file:
                    # Читаем содержимое ключа только если файл существует
                    if os.path.exists(self.ssh_key_file):
                        # Если задан пароль для ключа, используем его
                        if self.ssh_key_password:
                            tunnel_params["ssh_pkey"] = self.ssh_key_file
                            tunnel_params["ssh_private_key_password"] = (
                                self.ssh_key_password
                            )
                            print("Используем аутентификацию по ключу с паролем.")
                        else:
                            # Проверяем, защищен ли ключ паролем
                            try:
                                import paramiko

                                try:
                                    key = paramiko.RSAKey.from_private_key_file(
                                        self.ssh_key_file
                                    )
                                    tunnel_params["ssh_pkey"] = self.ssh_key_file
                                    print(
                                        "Используем аутентификацию по ключу без пароля."
                                    )
                                except paramiko.ssh_exception.PasswordRequiredException:
                                    # Ключ защищен паролем, но пароль не предоставлен
                                    print(
                                        "SSH ключ защищен паролем, но пароль не предоставлен."
                                    )
                                    # Используем только пароль, если он есть
                                    if self.ssh_password:
                                        print(
                                            "Используем аутентификацию по паролю вместо ключа."
                                        )
                                    else:
                                        print(
                                            "ВНИМАНИЕ: Не найдено подходящих методов аутентификации."
                                        )
                            except ImportError:
                                # Если paramiko не установлен, просто используем ключ как есть
                                tunnel_params["ssh_pkey"] = self.ssh_key_file
                                print(
                                    "Используем ключ без проверки защиты паролем (paramiko не установлен)."
                                )
                elif self.ssh_password:
                    tunnel_params["ssh_password"] = self.ssh_password
                    print("Используем аутентификацию по паролю (fallback).")
                else:
                    print("❌ ВНИМАНИЕ: Не найдено ни SSH ключа, ни пароля для аутентификации!")
                    print(f"ssh_key_content: {'есть' if self.ssh_key_content else 'нет'}")
                    print(f"ssh_key_file: {'есть' if self.ssh_key_file else 'нет'}")
                    print(f"ssh_password: {'есть' if self.ssh_password else 'нет'}")
                    
                    # Диагностика переменных окружения
                    print("🔍 Диагностика переменных окружения:")
                    ssh_private_key_env = os.getenv("SSH_PRIVATE_KEY")
                    print(f"SSH_PRIVATE_KEY env: {'есть' if ssh_private_key_env else 'нет'}")
                    if ssh_private_key_env:
                        print(f"SSH_PRIVATE_KEY длина: {len(ssh_private_key_env)} символов")
                    
                    ssh_host_env = os.getenv("SSH_HOST")
                    ssh_user_env = os.getenv("SSH_USER")
                    print(f"SSH_HOST env: {ssh_host_env}")
                    print(f"SSH_USER env: {ssh_user_env}")
                    
                    # НЕ поднимаем исключение, т.к. иногда SSH может работать без явной аутентификации
                    print("Пробуем создать туннель без явной аутентификации...")

                # Создаем туннель
                print(
                    f"Создание SSH-туннеля с параметрами: {tuple(tunnel_params.keys())}"
                )
                
                # Добавляем диагностику подключения
                print(f"🔗 Попытка подключения к SSH серверу:")
                print(f"   Host: {self.ssh_host}")
                print(f"   Port: {self.ssh_port}")
                print(f"   User: {self.ssh_username}")
                print(f"   Auth method: {'private_key' if 'ssh_pkey' in tunnel_params else 'password' if 'ssh_password' in tunnel_params else 'none'}")
                
                # Проверяем доступность SSH хоста перед созданием туннеля
                try:
                    import socket
                    print(f"🔍 Проверка доступности SSH хоста {self.ssh_host}:{self.ssh_port}...")
                    
                    # Сначала проверяем DNS разрешение
                    try:
                        ip_address = socket.gethostbyname(self.ssh_host)
                        print(f"✅ DNS разрешение: {self.ssh_host} -> {ip_address}")
                    except socket.gaierror as e:
                        print(f"❌ DNS разрешение не удалось: {e}")
                        print(f"🔍 Хост {self.ssh_host} не может быть разрешен в IP адрес")
                        raise
                    
                    # Проверяем TCP подключение
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)  # 10 секунд таймаут
                    result = sock.connect_ex((self.ssh_host, self.ssh_port))
                    sock.close()
                    
                    if result == 0:
                        print(f"✅ SSH хост {self.ssh_host}:{self.ssh_port} доступен")
                    else:
                        print(f"❌ SSH хост {self.ssh_host}:{self.ssh_port} НЕ доступен (код ошибки: {result})")
                        print(f"🔍 Это может означать что:")
                        print(f"   - Хост неправильный или не существует")
                        print(f"   - Порт {self.ssh_port} заблокирован фаерволом")
                        print(f"   - SSH сервис не запущен на хосте или на другом порту")
                except Exception as e:
                    print(f"❌ Ошибка при проверке доступности SSH хоста: {e}")
                
                self.tunnel = sshtunnel.SSHTunnelForwarder(**tunnel_params)
                print(f"🚀 Запуск SSH туннеля...")
                self.tunnel.start()
                print(f"✅ SSH туннель запущен, локальный порт: {self.tunnel.local_bind_port}")

                # Подключаемся к базе через туннель
                self.connection = psycopg2.connect(
                    host="127.0.0.1",
                    port=self.tunnel.local_bind_port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )
            else:
                # Обычное подключение без туннеля
                self.connection = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )

            if self.connection:
                self.cursor = self.connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor
                )
                print("Соединение с PostgreSQL установлено")
        except Error as e:
            print(f"Ошибка соединения с базой данных: {e}")
            if self.tunnel and self.tunnel.is_active:
                self.tunnel.close()
            raise

    def execute_query(self, query: str, params: Tuple = ()):
        """
        Выполняет запрос к базе данных.
        :param query: SQL-запрос.
        :param params: Параметры запроса.
        """
        if self.connection is None or self.connection.closed:
            raise RuntimeError("Соединение не установлено.")
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(("SELECT", "SHOW")):
                result = self.cursor.fetchall()
                # Преобразуем результат в список словарей
                columns = [desc[0] for desc in self.cursor.description]
                return [dict(zip(columns, row)) for row in result]
            return []
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            raise

    def commit(self):
        """Сохраняет изменения в базе данных."""
        if self.connection is not None and not self.connection.closed:
            try:
                self.connection.commit()
                print("Изменения сохранены.")
            except Error as e:
                print(f"Ошибка при сохранении изменений: {e}")
                self.connection.rollback()
                raise
        else:
            raise RuntimeError("Соединение не установлено или потеряно.")

    def rollback(self):
        """Откат транзакции"""
        try:
            self.connection.rollback()
        except Error as e:
            print(f"Ошибка в откате транзакции: {e}")

    def begin(self):
        if self.connection is not None and not self.connection.closed:
            try:
                self.connection.autocommit = False
                # В PostgreSQL транзакция начинается автоматически
            except Error as e:
                print(f"Ошибка при старте транзакции: {e}")
        else:
            raise RuntimeError("Соединение не установлено или потеряно.")

    def disconnect(self):
        """Закрывает соединение с базой данных PostgreSQL."""
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None and not self.connection.closed:
            self.connection.close()
        if self.tunnel and self.tunnel.is_active:
            self.tunnel.close()
        
        # Удаляем временный файл ключа если он был создан
        if self.temp_key_path and os.path.exists(self.temp_key_path):
            try:
                os.unlink(self.temp_key_path)
                print(f"Временный файл ключа удален: {self.temp_key_path}")
            except Exception as e:
                print(f"Ошибка при удалении временного файла ключа: {e}")
        
        self.connection = None
        self.cursor = None
        self.tunnel = None
        self.temp_key_path = None
        print("Соединение с PostgreSQL закрыто")


# Для обратной совместимости
MySQLDatabaseManager = PostgreSQLDatabaseManager
