from util.db.db_service import PostgreSQLDatabaseManager
import os
from dotenv import load_dotenv
import traceback

# Загружаем переменные окружения
load_dotenv()


class DBQuery:
    def __init__(self):
        try:
            # Получаем параметры подключения из переменных окружения
            host = os.getenv("DB_HOST")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            database = os.getenv("DB_NAME")
            # port = os.getenv("PORT", "5432")

            # Получаем параметры SSH-туннеля, если они есть
            ssh_host = os.getenv("SSH_HOST")
            ssh_user = os.getenv("SSH_USER")
            ssh_password = os.getenv("SSH_PASSWORD")
            ssh_key_file = os.getenv("SSH_KEY_FILE")
            ssh_key_password = os.getenv("SSH_KEY_PASSWORD")  # Пароль для SSH-ключа

            # Проверяем, что все необходимые параметры установлены
            if not all([host, user, password, database]):
                missing = []
                if not host:
                    missing.append("DB_HOST")
                if not user:
                    missing.append("DB_USER")
                if not password:
                    missing.append("DB_PASSWORD")
                if not database:
                    missing.append("DB_NAME")
                print(f"ОШИБКА: Отсутствуют переменные окружения: {', '.join(missing)}")

            # Выводим параметры подключения (без пароля)
            print(
                f"Параметры подключения к БД: HOST={host}, DB_USER={user}, DATABASE={database}"
            )

            # Определяем, используем ли SSH-туннель
            if ssh_host:
                print(f"Используется SSH-туннель через хост: {ssh_host}")
                self.db_manager = PostgreSQLDatabaseManager(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    ssh_host=ssh_host,
                    ssh_username=ssh_user,
                    ssh_password=ssh_password,
                    ssh_key_file=ssh_key_file,
                    ssh_key_password=ssh_key_password,  # Передаем пароль от SSH-ключа
                )
            else:
                # Используем локальное подключение
                self.db_manager = PostgreSQLDatabaseManager(
                    host=host, user=user, password=password, database=database
                )
        except Exception as e:
            print(f"Ошибка при инициализации DBQuery: {e}")
            traceback.print_exc()
            raise

    def get_list_column_from_query(self, query, args=None):
        """
        Метод для получения списка значений из запроса.
        :param query: SQL-запрос
        :param args: Аргументы запроса
        :return: Список значений
        """
        try:
            self.db_manager.connect()
            result = self.db_manager.execute_query(query=query, params=args)
            return [list(row.values())[0] for row in result] if result else []
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            self.db_manager.disconnect()

    def get_single_string_column_from_query(self, query: str, params: tuple):
        try:
            self.db_manager.connect()
            print(f"SQL запрос: {query}")
            print(f"Параметры: {params}")
            result = self.db_manager.execute_query(query=query, params=params)
            if not result:
                print("Запрос не вернул результатов.")
                return None

            first_row = result[0]

            if len(first_row) == 0:
                print("Результат запроса не содержит столбцов.")
                return None

            value = list(first_row.values())[0]
            # Не логируем само значение - запрос может вернуть чувствительные
            # данные (например otp_secret), а этот метод универсальный
            print("Значение успешно получено из БД")
            return value
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            traceback.print_exc()
            return None
        finally:
            try:
                self.db_manager.disconnect()
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")

    def execute_query_with_commit(self, query: str, params: tuple):
        try:
            self.db_manager.connect()
            self.db_manager.execute_query(query=query, params=params)
            self.db_manager.commit()
        except Exception as e:
            print(f"Ошибка при выполнении запроса с коммитом: {e}")
            traceback.print_exc()
        finally:
            self.db_manager.disconnect()

    def begin_transaction(self):
        """Метод для начала транзакции."""
        try:
            self.db_manager.connect()  # Устанавливаем соединение
            self.db_manager.begin()  # Начинаем транзакцию
        except Exception as e:
            print(f"Ошибка при начале транзакции: {e}")
            traceback.print_exc()
            self.db_manager.disconnect()

    def commit_transaction(self):
        """Метод для подтверждения транзакции."""
        try:
            self.db_manager.commit()  # Подтверждаем все изменения
        except Exception as e:
            print(f"Ошибка при коммите транзакции: {e}")
            traceback.print_exc()

    def rollback_transaction(self):
        """Метод для отката транзакции."""
        try:
            self.db_manager.rollback()  # Откатываем изменения
        except Exception as e:
            print(f"Ошибка при откате транзакции: {e}")
            traceback.print_exc()
        finally:
            self.db_manager.disconnect()  # Закрываем соединение после отката

    # Методы для каскадного удаления данных
    
    def delete_user_cascade_by_email(self, email: str, dry_run: bool = True):
        """
        Каскадное удаление пользователя и всех связанных данных по email
        :param email: Email пользователя для удаления
        :param dry_run: Если True, только показывает что будет удалено без фактического удаления
        :return: True если успешно, False при ошибке
        """
        from util.db.db_queries import DBQueries
        
        try:
            # Получаем ID пользователя
            user_id = self.get_single_string_column_from_query(
                DBQueries.get_user_id_by_email(), (email,)
            )
            
            if not user_id:
                print(f"Пользователь с email '{email}' не найден")
                return False
            
            print(f"Найден пользователь ID: {user_id}, Email: {email}")
            
            if dry_run:
                # Показываем что будет удалено
                print("=== РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА ===")
                related_data = self.get_list_column_from_query(
                    DBQueries.get_user_related_data_count(), 
                    tuple([user_id] * 8)
                )
                
                print("Связанные данные для удаления:")
                for data in related_data:
                    print(f"  - {data}")
                    
                print("Для фактического удаления запустите с dry_run=False")
                return True
            
            # Фактическое удаление
            print("=== ВЫПОЛНЯЕТСЯ КАСКАДНОЕ УДАЛЕНИЕ ===")
            self.begin_transaction()
            
            # Выполняем каскадное удаление
            query = DBQueries.delete_user_cascade()
            # Передаем user_id для каждого %s в запросе (25 параметров)
            # 11 обычных user_id + 2 для receiptsignature + 2 для receipts + 2 для подписей + 2 external_id + 1 author_id + 2 contract удаления + строка сессии + 1 admin_log + 1 final user_id
            params = tuple([user_id] * 11 + [user_id] * 2 + [user_id] * 2 + [user_id] * 2 + [str(user_id)] * 2 + [user_id] + [user_id] * 2 + [f'%{user_id}%'] + [user_id] * 2)
            
            self.db_manager.execute_query(query=query, params=params)
            self.commit_transaction()
            
            print(f"Пользователь {email} (ID: {user_id}) и все связанные данные успешно удалены")
            return True
            
        except Exception as e:
            print(f"Ошибка при каскадном удалении пользователя: {e}")
            traceback.print_exc()
            self.rollback_transaction()
            return False
    
    def delete_test_users_cascade(self, dry_run: bool = True):
        """
        Удалить всех тестовых пользователей и связанные данные
        :param dry_run: Если True, только показывает что будет удалено
        :return: True если успешно, False при ошибке
        """
        from util.db.db_queries import DBQueries
        
        try:
            if dry_run:
                print("=== РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА ===")
                test_users = self.get_list_column_from_query(
                    "SELECT email FROM users_user WHERE email LIKE '%test%' OR email LIKE '%demo%' OR email LIKE '%@example.%'",
                    ()
                )
                
                if not test_users:
                    print("Тестовые пользователи не найдены")
                    return True
                
                print(f"Найдено {len(test_users)} тестовых пользователей:")
                for email in test_users:
                    print(f"  - {email}")
                
                print("Для фактического удаления запустите с dry_run=False")
                return True
            
            # Фактическое удаление
            print("=== УДАЛЕНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ ===")
            self.begin_transaction()
            
            query = DBQueries.delete_test_users_cascade()
            self.db_manager.execute_query(query=query, params=())
            self.commit_transaction()
            
            print("Все тестовые пользователи и связанные данные успешно удалены")
            return True
            
        except Exception as e:
            print(f"Ошибка при удалении тестовых пользователей: {e}")
            traceback.print_exc()
            self.rollback_transaction()
            return False
    
    def clean_logs_tables(self, dry_run: bool = True):
        """
        Очистить таблицы логов
        :param dry_run: Если True, только показывает что будет удалено
        :return: True если успешно, False при ошибке
        """
        from util.db.db_queries import DBQueries
        
        try:
            if dry_run:
                print("=== РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА ===")
                
                # Проверяем количество записей в логах
                log_tables = ['django_admin_log', 'django_session', 'token_blacklist_outstandingtoken', 'token_blacklist_blacklistedtoken']
                for table in log_tables:
                    try:
                        count = self.get_single_string_column_from_query(
                            f"SELECT COUNT(*) FROM {table}", ()
                        )
                        print(f"Таблица {table}: {count} записей")
                    except:
                        print(f"Таблица {table}: не существует или недоступна")
                
                print("Для фактической очистки запустите с dry_run=False")
                return True
            
            # Фактическая очистка
            print("=== ОЧИСТКА ТАБЛИЦ ЛОГОВ ===")
            self.begin_transaction()
            
            query = DBQueries.truncate_logs_tables()
            self.db_manager.execute_query(query=query, params=())
            self.commit_transaction()
            
            print("Таблицы логов успешно очищены")
            return True
            
        except Exception as e:
            print(f"Ошибка при очистке таблиц логов: {e}")
            traceback.print_exc()
            self.rollback_transaction()
            return False
    
    def set_user_kyc_status_by_email(self,
                                     email: str,
                                     kyc_status: str = "approved",
                                     firstname: str = "Test",
                                     lastname: str = "Testov"):
        """
        Проставить KYC статус пользователю по email
        :param lastname:
        :param firstname:
        :param email: Email пользователя
        :param kyc_status: Статус KYC (по умолчанию "approved")
        :return: True если успешно, False при ошибке
        """
        from util.db.db_queries import DBQueries
        
        try:
            # Получаем ID пользователя по email
            user_id = self.get_single_string_column_from_query(
                DBQueries.get_user_id_by_email(), (email,)
            )
            
            if not user_id:
                print(f"Пользователь с email '{email}' не найден")
                return False
            
            print(f"Найден пользователь ID: {user_id}, Email: {email}")

            # Проставляем Имя
            self.execute_query_with_commit(
                DBQueries.update_user_firstname(),
                (firstname, user_id)
            )

            # Проставляем фамилию
            self.execute_query_with_commit(
                DBQueries.update_user_lastname(),
                (lastname, user_id)
            )
            
            # Проставляем KYC статус
            self.execute_query_with_commit(
                DBQueries.update_user_kyc_status(), 
                (kyc_status, user_id)
            )
            
            print(f"KYC статус '{kyc_status}' успешно проставлен пользователю {email} (ID: {user_id})")
            return True
            
        except Exception as e:
            print(f"Ошибка при проставлении KYC статуса: {e}")
            traceback.print_exc()
            return False

 