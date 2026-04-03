"""
Account Verification Module
Converted from COBOL program ACCOUNT-VERIFY.
"""


class AccountRecord:
    """Represents a stored account record (equivalent to WS-ACCOUNT-RECORD)."""

    def __init__(self, account_no: str, pin: str, status: str):
        self.account_no = account_no
        self.pin = pin
        self.status = status


# Default account store (mirrors the hardcoded COBOL values)
DEFAULT_ACCOUNTS = [
    AccountRecord(account_no="1234567890", pin="4321", status="ACTIVE"),
]


class AccountVerifier:
    """Performs three-tier account verification."""

    def __init__(self, accounts: list[AccountRecord] | None = None):
        self.accounts = accounts if accounts is not None else DEFAULT_ACCOUNTS

    def verify(self, account_no: str, pin: str) -> str:
        """
        Verify an account using the same three-gate logic as the COBOL program:
        1. Check account existence
        2. Check account status is ACTIVE
        3. Check PIN matches

        Returns one of:
          - "ACCOUNT NOT FOUND"
          - "ACCOUNT NOT ACTIVE"
          - "ACCOUNT VERIFIED"
          - "INVALID PIN"
        """
        # Gate 1: Account existence
        record = self._find_account(account_no)
        if record is None:
            return "ACCOUNT NOT FOUND"

        # Gate 2: Account status
        if record.status != "ACTIVE":
            return "ACCOUNT NOT ACTIVE"

        # Gate 3: PIN authentication
        if pin == record.pin:
            return "ACCOUNT VERIFIED"
        else:
            return "INVALID PIN"

    def _find_account(self, account_no: str) -> AccountRecord | None:
        for record in self.accounts:
            if record.account_no == account_no:
                return record
        return None


def main():
    """Console entry point -- mirrors MAIN-PARA from the COBOL program."""
    verifier = AccountVerifier()

    account_no = input("ENTER ACCOUNT NUMBER: ").strip()
    pin = input("ENTER PIN: ").strip()

    result = verifier.verify(account_no, pin)
    print(result)


if __name__ == "__main__":
    main()
