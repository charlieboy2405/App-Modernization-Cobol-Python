"""Account verification logic - Direct conversion of COBOL PROCEDURE DIVISION.

This module converts the COBOL ACCOUNT-VERIFY program's VERIFY-ACCOUNT paragraph
into Python. The logic faithfully preserves the original COBOL verification flow:

COBOL VERIFY-ACCOUNT paragraph:
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
            END-IF
        END-IF
    END-IF.
"""

from app.models import (
    AccountInput,
    AccountRecord,
    AccountStatus,
    VerificationMessage,
    VerificationResult,
)

# Default account record simulating COBOL WORKING-STORAGE hardcoded values
DEFAULT_ACCOUNT_RECORD = AccountRecord(
    stored_account="1234567890",
    stored_pin="4321",
    status=AccountStatus.ACTIVE,
)


def verify_account(
    account_input: AccountInput,
    account_record: AccountRecord | None = None,
) -> VerificationResult:
    """Verify an account against stored credentials.

    Direct conversion of COBOL VERIFY-ACCOUNT paragraph.
    Preserves the exact same nested IF-ELSE logic flow.

    Args:
        account_input: User-provided account number and PIN (COBOL WS-INPUT).
        account_record: Stored account record to verify against (COBOL WS-ACCOUNT-RECORD).
                       Defaults to the hardcoded record matching the original COBOL program.

    Returns:
        VerificationResult with the appropriate message.
    """
    if account_record is None:
        account_record = DEFAULT_ACCOUNT_RECORD

    # COBOL: IF WS-ACCOUNT-NO NOT = WS-STORED-ACCOUNT
    if account_input.account_no != account_record.stored_account:
        return VerificationResult(
            message=VerificationMessage.ACCOUNT_NOT_FOUND,
            success=False,
        )

    # COBOL: IF WS-STATUS NOT = "ACTIVE"
    if account_record.status != AccountStatus.ACTIVE:
        return VerificationResult(
            message=VerificationMessage.ACCOUNT_NOT_ACTIVE,
            success=False,
        )

    # COBOL: IF WS-PIN = WS-STORED-PIN
    if account_input.pin == account_record.stored_pin:
        return VerificationResult(
            message=VerificationMessage.ACCOUNT_VERIFIED,
            success=True,
        )

    # COBOL: ELSE (PIN mismatch)
    return VerificationResult(
        message=VerificationMessage.INVALID_PIN,
        success=False,
    )
