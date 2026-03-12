"""
Account Verification Module

Converted from COBOL program ACCOUNT-VERIFY.
This module provides account verification functionality including
account number lookup, account status checking, and PIN validation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VerificationResult(Enum):
    """Possible outcomes of account verification."""

    ACCOUNT_NOT_FOUND = "ACCOUNT NOT FOUND"
    ACCOUNT_NOT_ACTIVE = "ACCOUNT NOT ACTIVE"
    INVALID_PIN = "INVALID PIN"
    ACCOUNT_VERIFIED = "ACCOUNT VERIFIED"


@dataclass
class AccountRecord:
    """Represents a stored account record."""

    account_no: str
    pin: str
    status: str

    def is_active(self) -> bool:
        """Check if the account status is ACTIVE."""
        return self.status.upper() == "ACTIVE"


class AccountVerifier:
    """
    Verifies account credentials against stored account records.

    Mirrors the COBOL ACCOUNT-VERIFY program logic:
    1. Check if the account number exists.
    2. Check if the account is active.
    3. Validate the PIN.
    """

    def __init__(self, accounts: Optional[list[AccountRecord]] = None):
        """
        Initialize with a list of account records.

        If no accounts are provided, a default account is used
        (matching the original COBOL hardcoded values).
        """
        if accounts is None:
            self._accounts = [
                AccountRecord(
                    account_no="1234567890",
                    pin="4321",
                    status="ACTIVE",
                )
            ]
        else:
            self._accounts = list(accounts)

    def _find_account(self, account_no: str) -> Optional[AccountRecord]:
        """Look up an account by account number."""
        for account in self._accounts:
            if account.account_no == account_no:
                return account
        return None

    def verify(self, account_no: str, pin: str) -> VerificationResult:
        """
        Verify an account number and PIN combination.

        Args:
            account_no: The account number to verify (up to 10 characters).
            pin: The PIN to validate (up to 4 characters).

        Returns:
            VerificationResult indicating the outcome.
        """
        account = self._find_account(account_no)

        if account is None:
            return VerificationResult.ACCOUNT_NOT_FOUND

        if not account.is_active():
            return VerificationResult.ACCOUNT_NOT_ACTIVE

        if pin == account.pin:
            return VerificationResult.ACCOUNT_VERIFIED
        else:
            return VerificationResult.INVALID_PIN


def main() -> None:
    """
    CLI entry point mirroring the original COBOL interactive flow.

    Prompts the user for an account number and PIN, then displays
    the verification result.
    """
    verifier = AccountVerifier()

    account_no = input("ENTER ACCOUNT NUMBER: ").strip()
    pin = input("ENTER PIN: ").strip()

    result = verifier.verify(account_no, pin)
    print(result.value)


if __name__ == "__main__":
    main()
