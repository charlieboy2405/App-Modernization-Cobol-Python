"""Tests for account verification logic - validates COBOL VERIFY-ACCOUNT conversion.

These tests comprehensively verify that the Python conversion produces
identical results to the original COBOL VERIFY-ACCOUNT paragraph for
all possible verification paths:

1. Account not found (WS-ACCOUNT-NO != WS-STORED-ACCOUNT)
2. Account not active (WS-STATUS != "ACTIVE")
3. Account verified (all checks pass, PIN matches)
4. Invalid PIN (account found & active, but PIN mismatch)
"""

import pytest

from app.account_verify import DEFAULT_ACCOUNT_RECORD, verify_account
from app.models import (
    AccountInput,
    AccountRecord,
    AccountStatus,
    VerificationMessage,
)


class TestVerifyAccountSuccess:
    """Tests for successful account verification (COBOL: ACCOUNT VERIFIED)."""

    def test_valid_credentials(self) -> None:
        """Exact match of hardcoded COBOL credentials: account=1234567890, pin=4321."""
        inp = AccountInput(account_no="1234567890", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_VERIFIED
        assert result.success is True
        assert result.result_text == "ACCOUNT VERIFIED"

    def test_valid_credentials_with_default_record(self) -> None:
        """Verify against explicitly provided default record."""
        inp = AccountInput(account_no="1234567890", pin="4321")
        result = verify_account(inp, DEFAULT_ACCOUNT_RECORD)
        assert result.message == VerificationMessage.ACCOUNT_VERIFIED
        assert result.success is True

    def test_valid_credentials_custom_record(self) -> None:
        """Verify against a custom account record."""
        record = AccountRecord(
            stored_account="ABCDEFGHIJ",
            stored_pin="9999",
            status=AccountStatus.ACTIVE,
        )
        inp = AccountInput(account_no="ABCDEFGHIJ", pin="9999")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_VERIFIED
        assert result.success is True


class TestVerifyAccountNotFound:
    """Tests for account not found (COBOL: WS-ACCOUNT-NO NOT = WS-STORED-ACCOUNT)."""

    def test_wrong_account_number(self) -> None:
        inp = AccountInput(account_no="0000000000", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False
        assert result.result_text == "ACCOUNT NOT FOUND"

    def test_empty_account_number(self) -> None:
        inp = AccountInput(account_no="", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False

    def test_partial_account_number(self) -> None:
        """Partial match should still fail - COBOL uses exact string comparison."""
        inp = AccountInput(account_no="12345", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False

    def test_account_with_extra_chars(self) -> None:
        inp = AccountInput(account_no="12345678901", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False

    def test_account_with_spaces(self) -> None:
        """COBOL PIC X fields are space-padded; Python uses exact match."""
        inp = AccountInput(account_no="1234567890 ", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False

    def test_case_sensitive_account(self) -> None:
        """COBOL string comparison is case-sensitive."""
        inp = AccountInput(account_no="abcdefghij", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False


class TestVerifyAccountNotActive:
    """Tests for inactive account (COBOL: WS-STATUS NOT = 'ACTIVE')."""

    def test_inactive_account(self) -> None:
        record = AccountRecord(
            stored_account="1234567890",
            stored_pin="4321",
            status=AccountStatus.INACTIVE,
        )
        inp = AccountInput(account_no="1234567890", pin="4321")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_NOT_ACTIVE
        assert result.success is False
        assert result.result_text == "ACCOUNT NOT ACTIVE"

    def test_suspended_account(self) -> None:
        record = AccountRecord(
            stored_account="1234567890",
            stored_pin="4321",
            status=AccountStatus.SUSPENDED,
        )
        inp = AccountInput(account_no="1234567890", pin="4321")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_NOT_ACTIVE
        assert result.success is False

    def test_inactive_account_wrong_pin(self) -> None:
        """Status check happens before PIN check, so ACCOUNT NOT ACTIVE takes precedence."""
        record = AccountRecord(
            stored_account="1234567890",
            stored_pin="4321",
            status=AccountStatus.INACTIVE,
        )
        inp = AccountInput(account_no="1234567890", pin="0000")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_NOT_ACTIVE
        assert result.success is False


class TestVerifyInvalidPin:
    """Tests for invalid PIN (COBOL: WS-PIN NOT = WS-STORED-PIN)."""

    def test_wrong_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="0000")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN
        assert result.success is False
        assert result.result_text == "INVALID PIN"

    def test_empty_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN
        assert result.success is False

    def test_partial_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="432")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN
        assert result.success is False

    def test_reversed_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="1234")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN
        assert result.success is False

    def test_pin_with_spaces(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="4321 ")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN
        assert result.success is False


class TestVerifyAccountPrecedence:
    """Tests for verification check order - must match COBOL nested IF-ELSE order.

    COBOL checks: 1) Account number, 2) Status, 3) PIN
    Each level is only reached if the previous check passes.
    """

    def test_wrong_account_takes_precedence_over_inactive(self) -> None:
        """Account check is first, so wrong account returns NOT FOUND even if inactive."""
        record = AccountRecord(
            stored_account="1234567890",
            stored_pin="4321",
            status=AccountStatus.INACTIVE,
        )
        inp = AccountInput(account_no="0000000000", pin="4321")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND

    def test_wrong_account_takes_precedence_over_wrong_pin(self) -> None:
        inp = AccountInput(account_no="0000000000", pin="0000")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND

    def test_inactive_takes_precedence_over_wrong_pin(self) -> None:
        """Status check is second, so inactive returns NOT ACTIVE even if PIN is wrong."""
        record = AccountRecord(
            stored_account="1234567890",
            stored_pin="4321",
            status=AccountStatus.INACTIVE,
        )
        inp = AccountInput(account_no="1234567890", pin="0000")
        result = verify_account(inp, record)
        assert result.message == VerificationMessage.ACCOUNT_NOT_ACTIVE


class TestDefaultAccountRecord:
    """Tests for the module-level DEFAULT_ACCOUNT_RECORD constant."""

    def test_matches_cobol_values(self) -> None:
        """Must match the COBOL WORKING-STORAGE VALUE clauses exactly."""
        assert DEFAULT_ACCOUNT_RECORD.stored_account == "1234567890"
        assert DEFAULT_ACCOUNT_RECORD.stored_pin == "4321"
        assert DEFAULT_ACCOUNT_RECORD.status == AccountStatus.ACTIVE


class TestEdgeCases:
    """Edge case tests for robustness."""

    def test_numeric_strings(self) -> None:
        """COBOL PIC X fields store alphanumeric data as strings."""
        inp = AccountInput(account_no="1234567890", pin="4321")
        result = verify_account(inp)
        assert result.success is True

    def test_special_characters_in_account(self) -> None:
        inp = AccountInput(account_no="!@#$%^&*()", pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND

    def test_special_characters_in_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="!@#$")
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN

    def test_unicode_account(self) -> None:
        unicode_account = "\u00e9\u00e8\u00ea\u00eb\u00e0\u00e1\u00e2\u00e3\u00e4\u00e5"
        inp = AccountInput(account_no=unicode_account, pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND

    def test_very_long_account(self) -> None:
        inp = AccountInput(account_no="A" * 100, pin="4321")
        result = verify_account(inp)
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND

    def test_very_long_pin(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="9" * 100)
        result = verify_account(inp)
        assert result.message == VerificationMessage.INVALID_PIN

    @pytest.mark.parametrize(
        "account_no,pin,expected_message",
        [
            ("1234567890", "4321", VerificationMessage.ACCOUNT_VERIFIED),
            ("0000000000", "4321", VerificationMessage.ACCOUNT_NOT_FOUND),
            ("1234567890", "0000", VerificationMessage.INVALID_PIN),
            ("", "", VerificationMessage.ACCOUNT_NOT_FOUND),
            ("1234567890", "", VerificationMessage.INVALID_PIN),
            ("", "4321", VerificationMessage.ACCOUNT_NOT_FOUND),
        ],
    )
    def test_parametrized_scenarios(
        self,
        account_no: str,
        pin: str,
        expected_message: VerificationMessage,
    ) -> None:
        inp = AccountInput(account_no=account_no, pin=pin)
        result = verify_account(inp)
        assert result.message == expected_message
