"""CLI interface for Account Verification - Mirrors COBOL MAIN-PARA.

This module replicates the COBOL program's terminal-based I/O:

COBOL MAIN-PARA:
    DISPLAY "ENTER ACCOUNT NUMBER: ".
    ACCEPT WS-ACCOUNT-NO.
    DISPLAY "ENTER PIN: ".
    ACCEPT WS-PIN.
    PERFORM VERIFY-ACCOUNT.
    DISPLAY WS-RESULT.
    STOP RUN.
"""

from app.account_verify import verify_account
from app.models import AccountInput


def main() -> None:
    """Main entry point matching COBOL MAIN-PARA paragraph."""
    # COBOL: DISPLAY "ENTER ACCOUNT NUMBER: " / ACCEPT WS-ACCOUNT-NO
    account_no = input("ENTER ACCOUNT NUMBER: ")

    # COBOL: DISPLAY "ENTER PIN: " / ACCEPT WS-PIN
    pin = input("ENTER PIN: ")

    # COBOL: PERFORM VERIFY-ACCOUNT
    account_input = AccountInput(account_no=account_no, pin=pin)
    result = verify_account(account_input)

    # COBOL: DISPLAY WS-RESULT
    print(result.result_text)


if __name__ == "__main__":
    main()
