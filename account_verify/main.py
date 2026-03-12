"""
CLI entry point for the Account Verification program.

Mirrors the COBOL MAIN-PARA paragraph:
    DISPLAY "ENTER ACCOUNT NUMBER: ".
    ACCEPT WS-ACCOUNT-NO.
    DISPLAY "ENTER PIN: ".
    ACCEPT WS-PIN.
    PERFORM VERIFY-ACCOUNT.
    DISPLAY WS-RESULT.
    STOP RUN.
"""

import sys

from account_verify.account_verify import verify_account


def main() -> None:
    """Run the interactive account verification prompt."""
    try:
        account_no = input("ENTER ACCOUNT NUMBER: ")
        pin = input("ENTER PIN: ")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)

    result = verify_account(account_no, pin)
    print(result)


if __name__ == "__main__":
    main()
