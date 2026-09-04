class Users:

    def __init__(
            self,
            email: str = None,
            password: str = None,
            first_name: str = None,
            last_name: str = None,
            birth_day=None,
            nick_name: str = None,
            country_id: str = None,
    ):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.birth_day = birth_day
        self.nick_name = nick_name
        self.country_id = country_id


WRONG_EMAIL = Users(email="wrong_email")
NOT_CREATE_EMAIL = Users(email="not_create_email@gmail.com")
TEST_LOGIN = Users(email="test_login@example-payroll.com")
MANAGER = Users(email="manager@example-payroll.com")
TEST_WORKER = Users(email="test_worker@example-payroll.com")
TEST_ONBOARDING = Users(email="test_onboarding@example-payroll.com")
TEST_LOGOUT = Users(email="test_logout@example-payroll.com")
TEST_CONFIRM_KYC = Users(email="test_confirm_kyc@example-payroll.com")
TEST_FILL_ADDRESS = Users(email="test_fill_address@example-payroll.com")



