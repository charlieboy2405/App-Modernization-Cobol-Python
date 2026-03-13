"""Data models for the Account Verification service.

Direct conversion of COBOL WORKING-STORAGE SECTION data structures:
- WS-INPUT -> AccountInput (account_no, pin)
- WS-ACCOUNT-RECORD -> AccountRecord (stored_account, stored_pin, status)
- WS-RESULT -> VerificationResult (result message)
"""

from dataclasses import dataclass, field
from enum import Enum


class AccountStatus(Enum):
    """Account status values."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class VerificationMessage(Enum):
    """Verification result messages matching COBOL WS-RESULT values."""

    ACCOUNT_VERIFIED = "ACCOUNT VERIFIED"
    ACCOUNT_NOT_FOUND = "ACCOUNT NOT FOUND"
    ACCOUNT_NOT_ACTIVE = "ACCOUNT NOT ACTIVE"
    INVALID_PIN = "INVALID PIN"


@dataclass
class AccountInput:
    """Corresponds to COBOL 01 WS-INPUT group.

    05 WS-ACCOUNT-NO  PIC X(10) -> account_no: str (max 10 chars)
    05 WS-PIN         PIC X(4)  -> pin: str (max 4 chars)
    """

    account_no: str
    pin: str


@dataclass
class AccountRecord:
    """Corresponds to COBOL 01 WS-ACCOUNT-RECORD group.

    05 WS-STORED-ACCOUNT PIC X(10) VALUE "1234567890" -> stored_account
    05 WS-STORED-PIN     PIC X(4)  VALUE "4321"       -> stored_pin
    05 WS-STATUS         PIC X(10) VALUE "ACTIVE"      -> status
    """

    stored_account: str = "1234567890"
    stored_pin: str = "4321"
    status: AccountStatus = field(default=AccountStatus.ACTIVE)


@dataclass
class VerificationResult:
    """Corresponds to COBOL 01 WS-RESULT PIC X(30).

    Holds the outcome of account verification.
    """

    message: VerificationMessage
    success: bool

    @property
    def result_text(self) -> str:
        return self.message.value
