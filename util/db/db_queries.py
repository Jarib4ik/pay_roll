class DBQueries:
    """Класс с SQL запросами для тестирования"""

    @staticmethod
    def get_auth_otp_by_email():
        return "SELECT otp_secret FROM users_user WHERE email = %s"

    @staticmethod
    def get_user_id_by_email():
        """Получить ID пользователя по email"""
        return "SELECT id FROM users_user WHERE email = %s"

    @staticmethod
    def get_contract_id_by_manager():
        """Получить ID пользователя по email"""
        return "SELECT id FROM contracts_contract WHERE manager_id = %s"

    @staticmethod
    def get_contract_id_by_worker():
        """Получить ID пользователя по email"""
        return "SELECT id FROM contracts_contract WHERE customer_id = %s"

    @staticmethod
    def get_manager_signature_otp_by_contract_id():
        return "SELECT company_otp FROM contracts_contractsignature WHERE contract_id = %s"

    @staticmethod
    def get_worker_signature_otp_by_contract_id():
        return "SELECT contractor_otp FROM contracts_contractsignature WHERE contract_id = %s"

    @staticmethod
    def delete_user_cascade():
        """Каскадное удаление пользователя со всеми связанными данными"""
        return """
        -- Удаляем токены и сессии
        DELETE FROM token_blacklist_blacklistedtoken 
        WHERE token_id IN (SELECT id FROM token_blacklist_outstandingtoken WHERE user_id = %s);
        
        DELETE FROM token_blacklist_outstandingtoken WHERE user_id = %s;
        
        -- Удаляем профильные данные
        DELETE FROM user_profile WHERE user_id = %s;
        DELETE FROM user_withdraw_methods WHERE user_id = %s;
        
        -- Удаляем связи с компаниями
        DELETE FROM users_user_companies WHERE user_id = %s;
        DELETE FROM users_user_groups WHERE user_id = %s;
        DELETE FROM users_user_user_permissions WHERE user_id = %s;
        
        -- Удаляем действия пользователя
        DELETE FROM users_action WHERE user_id = %s;
        
        -- Удаляем цифровые сертификаты
        DELETE FROM users_digitalcertificate WHERE owner_id = %s;
        
        -- Удаляем заявки на вывод
        DELETE FROM withdraw_requests WHERE user_id = %s;
        
        -- Удаляем транзакции обмена (связь через withdraw_request_id)
        DELETE FROM exchange_transactions WHERE withdraw_request_id IN 
            (SELECT id FROM withdraw_requests WHERE user_id = %s);
        
        -- Удаляем контракты и связанные документы (правильный порядок каскадного удаления)
        -- Сначала удаляем подписи актов (receiptsignature), которые ссылаются на receipts
        DELETE FROM contracts_receiptsignature WHERE receipt_id IN (
            SELECT cr.id FROM contracts_receipt cr
            JOIN contracts_contract cc ON cr.contract_id = cc.id
            WHERE cc.manager_id = %s OR cc.customer_id = %s
        );
        -- Затем удаляем акты (receipts), которые ссылаются на контракты
        DELETE FROM contracts_receipt WHERE contract_id IN (
            SELECT id FROM contracts_contract WHERE manager_id = %s OR customer_id = %s
        );
        -- Затем удаляем подписи контрактов по contract_id
        DELETE FROM contracts_contractsignature WHERE contract_id IN (
            SELECT id FROM contracts_contract WHERE manager_id = %s OR customer_id = %s
        );
        -- Удаляем подписи по external_id (если есть)
        DELETE FROM contracts_contractsignature WHERE contractor_external_id = %s OR company_external_id = %s;
        -- Удаляем документы контрактов
        DELETE FROM contracts_document WHERE author_id = %s;
        -- Наконец удаляем сами контракты
        DELETE FROM contracts_contract WHERE manager_id = %s OR customer_id = %s;
        
        -- Удаляем сессии Django (по содержимому)
        DELETE FROM django_session WHERE session_data LIKE %s;
        
        -- Удаляем админ логи
        DELETE FROM django_admin_log WHERE user_id = %s;
        
        -- Удаляем самого пользователя
        DELETE FROM users_user WHERE id = %s;
        """

    @staticmethod
    def delete_test_users_cascade():
        """Удалить всех тестовых пользователей (с email содержащим 'test' или 'demo')"""
        return """
        -- Получаем ID тестовых пользователей
        WITH test_users AS (
            SELECT id FROM users_user 
            WHERE email LIKE '%test%' OR email LIKE '%demo%' OR email LIKE '%@example.%'
        )
        -- Удаляем связанные данные
        DELETE FROM token_blacklist_blacklistedtoken 
        WHERE token_id IN (
            SELECT ot.id FROM token_blacklist_outstandingtoken ot
            JOIN test_users tu ON ot.user_id = tu.id
        );
        
        DELETE FROM token_blacklist_outstandingtoken 
        WHERE user_id IN (SELECT id FROM test_users);
        
        DELETE FROM auth_log WHERE user_id IN (SELECT id FROM test_users);
        
        -- Удаляем тестовых пользователей
        DELETE FROM users_user 
        WHERE email LIKE '%test%' OR email LIKE '%demo%' OR email LIKE '%@example.%';
        """

    @staticmethod
    def truncate_logs_tables():
        """Очистить все таблицы логов"""
        return """
        TRUNCATE TABLE django_admin_log RESTART IDENTITY CASCADE;
        TRUNCATE TABLE django_session RESTART IDENTITY CASCADE;
        DELETE FROM token_blacklist_outstandingtoken;
        DELETE FROM token_blacklist_blacklistedtoken;
        """

    @staticmethod
    def get_user_related_data_count():
        """Подсчитать количество связанных данных пользователя"""
        return """
        SELECT 
            'tokens' as data_type, COUNT(*) as count 
        FROM token_blacklist_outstandingtoken WHERE user_id = %s
        UNION ALL
        SELECT 
            'profiles', COUNT(*) 
        FROM user_profile WHERE user_id = %s
        UNION ALL
        SELECT 
            'withdraw_methods', COUNT(*) 
        FROM user_withdraw_methods WHERE user_id = %s
        UNION ALL
        SELECT 
            'companies', COUNT(*) 
        FROM users_user_companies WHERE user_id = %s
        UNION ALL
        SELECT 
            'actions', COUNT(*) 
        FROM users_action WHERE user_id = %s
        UNION ALL
        SELECT 
            'withdraw_requests', COUNT(*) 
        FROM withdraw_requests WHERE user_id = %s
        UNION ALL
        SELECT 
            'exchange_transactions', COUNT(*) 
        FROM exchange_transactions WHERE withdraw_request_id IN 
            (SELECT id FROM withdraw_requests WHERE user_id = %s)
        UNION ALL
        SELECT 
            'admin_logs', COUNT(*) 
        FROM django_admin_log WHERE user_id = %s;
        """

    @staticmethod
    def update_user_kyc_status():
        """Обновить KYC статус пользователя в таблице user_profile по user_id"""
        return """
        UPDATE user_profile 
        SET kyc_status = %s 
        WHERE user_id = %s
        """

    @staticmethod
    def update_user_firstname():
        """Обновить First Name пользователя в таблице user_profile по user_id"""
        return """
            UPDATE user_profile 
            SET firstname = %s 
            WHERE user_id = %s
            """

    @staticmethod
    def update_user_lastname():
        """Обновить Last Name пользователя в таблице user_profile по user_id"""
        return """
            UPDATE user_profile 
            SET lastname = %s 
            WHERE user_id = %s
            """
