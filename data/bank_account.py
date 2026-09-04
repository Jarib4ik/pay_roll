class BankAccount:

    def __init__(
        self,
        first_name: str = None,
        last_name: str = None,
        city: str = None,
        street_line_1: str = None,
        iban: str = None,
        zip_code: str = None,
        account_number: str = None,
        bic_swift: str = None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.city = city
        self.street_line_1 = street_line_1
        self.iban = iban
        self.zip_code = zip_code
        self.account_number = account_number
        self.bic_swift = bic_swift


ITALY_REVOLUT = BankAccount(
    first_name="Test",
    last_name="Testov",
    city="Bishkek",
    street_line_1="st.Togolok Moldo 54a",
    iban="IT85Y0306974823100000006843",
    zip_code="720033",
)