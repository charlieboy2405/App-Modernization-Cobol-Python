"""
Core account verification logic.

Converted from COBOL program ACCOUNT-VERIFY.
Original COBOL source: Financial-Investment-Unit-Trust-COBOL-code-12th-Mar-2026.md

This module provides account verification functionality that checks:
1. Whether the account number exists in the system.
2. Whether the account status is ACTIVE.
3. Whether the provided PIN matches the stored PIN.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountRecord:
    """Represents a stored account record.

    Mirrors the COBOL WORKING-STORAGE SECTION's WS-ACCOUNT-RECORD:
        05 WS-STORED-ACCOUNT PIC X(10)
        05 WS-STORED-PIN     PIC X(4)
        05 WS-STATUS         PIC X(10)
    """

    account_no: str
    pin: str
    status: str


# Default account record matching the COBOL hardcoded values
DEFAULT_ACCOUNT = AccountRecord(
    account_no="1234567890",
    pin="4321",
    status="ACTIVE",
)


def verify_account(
    input_account_no: str,
    input_pin: str,
    stored_account: AccountRecord = DEFAULT_ACCOUNT,
) -> str:
    """Verify an account by checking account number, status, and PIN.

    Mirrors the COBOL VERIFY-ACCOUNT paragraph logic:
        IF WS-ACCOUNT-NO NOT = WS-STORED-ACCOUNT
            MOVE "ACCOUNT NOT FOUND" TO WS-RESULT
        ELSE
            IF WS-STATUS NOT = "ACTIVE"
                MOVE "ACCOUNT NOT ACTIVE" TO WS-RESULT
            ELSE
                IF WS-PIN = WS-STORED-PIN
                    MOVE "ACCOUNT VERIFIED" TO WS-RESULT
                ELSE
                    MOVE "INVALID PIN" TO WS-RESULT

    Args:
        input_account_no: The account number provided by the user.
        input_pin: The PIN provided by the user.
        stored_account: The account record to verify against.
            Defaults to DEFAULT_ACCOUNT.

    Returns:
        A string result indicating the verification outcome:
        - "ACCOUNT NOT FOUND"  if account number does not match.
        - "ACCOUNT NOT ACTIVE" if the account status is not "ACTIVE".
        - "ACCOUNT VERIFIED"   if the PIN matches.
        - "INVALID PIN"        if the PIN does not match.
    """
    if input_account_no != stored_account.account_no:
        return "ACCOUNT NOT FOUND"

    if stored_account.status != "ACTIVE":
        return "ACCOUNT NOT ACTIVE"

    if input_pin == stored_account.pin:
        return "ACCOUNT VERIFIED"

    return "INVALID PIN"
