"""
Comprehensive tests for the Account Verification module.

Tests cover all verification paths from the original COBOL program:
- Account not found
- Account not active
- Invalid PIN
- Account verified (success)

Additional tests cover edge cases, multiple accounts, and the
AccountRecord dataclass.
"""

from unittest.mock import patch
from account_verify import (
    AccountRecord,
    AccountVerifier,
    VerificationResult,
    main,
)


# ---------------------------------------------------------------------------
# AccountRecord tests
# ---------------------------------------------------------------------------


class TestAccountRecord:
    """Tests for the AccountRecord dataclass."""

    def test_create_record(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="ACTIVE")
        assert record.account_no == "1234567890"
        assert record.pin == "4321"
        assert record.status == "ACTIVE"

    def test_is_active_true(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="ACTIVE")
        assert record.is_active() is True

    def test_is_active_false(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="INACTIVE")
        assert record.is_active() is False

    def test_is_active_case_insensitive(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="active")
        assert record.is_active() is True

    def test_is_active_mixed_case(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="Active")
        assert record.is_active() is True

    def test_is_active_closed_status(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="CLOSED")
        assert record.is_active() is False

    def test_is_active_suspended_status(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="SUSPENDED")
        assert record.is_active() is False

    def test_is_active_empty_status(self):
        record = AccountRecord(account_no="1234567890", pin="4321", status="")
        assert record.is_active() is False


# ---------------------------------------------------------------------------
# VerificationResult enum tests
# ---------------------------------------------------------------------------


class TestVerificationResult:
    """Tests for the VerificationResult enum values."""

    def test_account_not_found_value(self):
        assert VerificationResult.ACCOUNT_NOT_FOUND.value == "ACCOUNT NOT FOUND"

    def test_account_not_active_value(self):
        assert VerificationResult.ACCOUNT_NOT_ACTIVE.value == "ACCOUNT NOT ACTIVE"

    def test_invalid_pin_value(self):
        assert VerificationResult.INVALID_PIN.value == "INVALID PIN"

    def test_account_verified_value(self):
        assert VerificationResult.ACCOUNT_VERIFIED.value == "ACCOUNT VERIFIED"

    def test_enum_members_count(self):
        assert len(VerificationResult) == 4


# ---------------------------------------------------------------------------
# AccountVerifier – default account tests (matching COBOL hardcoded values)
# ---------------------------------------------------------------------------


class TestAccountVerifierDefault:
    """Tests using the default account (COBOL hardcoded values)."""

    def setup_method(self):
        self.verifier = AccountVerifier()

    def test_successful_verification(self):
        result = self.verifier.verify("1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_VERIFIED

    def test_account_not_found(self):
        result = self.verifier.verify("0000000000", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_invalid_pin(self):
        result = self.verifier.verify("1234567890", "0000")
        assert result == VerificationResult.INVALID_PIN

    def test_wrong_account_correct_pin(self):
        result = self.verifier.verify("9999999999", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_empty_account_number(self):
        result = self.verifier.verify("", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_empty_pin(self):
        result = self.verifier.verify("1234567890", "")
        assert result == VerificationResult.INVALID_PIN

    def test_empty_account_and_pin(self):
        result = self.verifier.verify("", "")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_partial_account_number(self):
        result = self.verifier.verify("12345", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_partial_pin(self):
        result = self.verifier.verify("1234567890", "43")
        assert result == VerificationResult.INVALID_PIN

    def test_account_with_leading_spaces(self):
        result = self.verifier.verify("  1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_pin_with_trailing_spaces(self):
        result = self.verifier.verify("1234567890", "4321 ")
        assert result == VerificationResult.INVALID_PIN


# ---------------------------------------------------------------------------
# AccountVerifier – custom account tests
# ---------------------------------------------------------------------------


class TestAccountVerifierCustomAccounts:
    """Tests with custom account data."""

    def test_single_custom_account_verified(self):
        accounts = [AccountRecord("ABCDE12345", "9999", "ACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("ABCDE12345", "9999")
        assert result == VerificationResult.ACCOUNT_VERIFIED

    def test_inactive_account(self):
        accounts = [AccountRecord("1234567890", "4321", "INACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_ACTIVE

    def test_closed_account(self):
        accounts = [AccountRecord("1234567890", "4321", "CLOSED")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_ACTIVE

    def test_suspended_account(self):
        accounts = [AccountRecord("1234567890", "4321", "SUSPENDED")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_ACTIVE

    def test_multiple_accounts_first_found(self):
        accounts = [
            AccountRecord("1111111111", "1111", "ACTIVE"),
            AccountRecord("2222222222", "2222", "ACTIVE"),
            AccountRecord("3333333333", "3333", "ACTIVE"),
        ]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1111111111", "1111")
        assert result == VerificationResult.ACCOUNT_VERIFIED

    def test_multiple_accounts_last_found(self):
        accounts = [
            AccountRecord("1111111111", "1111", "ACTIVE"),
            AccountRecord("2222222222", "2222", "ACTIVE"),
            AccountRecord("3333333333", "3333", "ACTIVE"),
        ]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("3333333333", "3333")
        assert result == VerificationResult.ACCOUNT_VERIFIED

    def test_multiple_accounts_not_found(self):
        accounts = [
            AccountRecord("1111111111", "1111", "ACTIVE"),
            AccountRecord("2222222222", "2222", "ACTIVE"),
        ]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("9999999999", "1111")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_multiple_accounts_wrong_pin_for_correct_account(self):
        accounts = [
            AccountRecord("1111111111", "1111", "ACTIVE"),
            AccountRecord("2222222222", "2222", "ACTIVE"),
        ]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("2222222222", "1111")
        assert result == VerificationResult.INVALID_PIN

    def test_empty_accounts_list(self):
        verifier = AccountVerifier(accounts=[])
        result = verifier.verify("1234567890", "4321")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_inactive_account_wrong_pin_returns_not_active(self):
        """Status check takes priority over PIN check (matches COBOL logic)."""
        accounts = [AccountRecord("1234567890", "4321", "INACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1234567890", "0000")
        assert result == VerificationResult.ACCOUNT_NOT_ACTIVE


# ---------------------------------------------------------------------------
# Verification priority / ordering tests (matching COBOL IF-ELSE nesting)
# ---------------------------------------------------------------------------


class TestVerificationPriority:
    """
    Verify that the verification priority matches the original COBOL logic:
    1. Account lookup (outermost IF)
    2. Status check (middle IF)
    3. PIN validation (innermost IF)
    """

    def test_account_check_before_status_check(self):
        """A non-existent account returns ACCOUNT NOT FOUND regardless of status."""
        accounts = [AccountRecord("1111111111", "1111", "INACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("9999999999", "1111")
        assert result == VerificationResult.ACCOUNT_NOT_FOUND

    def test_status_check_before_pin_check(self):
        """An inactive account returns ACCOUNT NOT ACTIVE even with correct PIN."""
        accounts = [AccountRecord("1111111111", "1111", "INACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1111111111", "1111")
        assert result == VerificationResult.ACCOUNT_NOT_ACTIVE

    def test_all_valid(self):
        """All checks pass → ACCOUNT VERIFIED."""
        accounts = [AccountRecord("1111111111", "1111", "ACTIVE")]
        verifier = AccountVerifier(accounts)
        result = verifier.verify("1111111111", "1111")
        assert result == VerificationResult.ACCOUNT_VERIFIED


# ---------------------------------------------------------------------------
# CLI main() function tests
# ---------------------------------------------------------------------------


class TestMainCLI:
    """Tests for the interactive CLI entry point."""

    @patch("builtins.input", side_effect=["1234567890", "4321"])
    @patch("builtins.print")
    def test_main_verified(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("ACCOUNT VERIFIED")

    @patch("builtins.input", side_effect=["0000000000", "4321"])
    @patch("builtins.print")
    def test_main_account_not_found(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("ACCOUNT NOT FOUND")

    @patch("builtins.input", side_effect=["1234567890", "0000"])
    @patch("builtins.print")
    def test_main_invalid_pin(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("INVALID PIN")

    @patch("builtins.input", side_effect=["  1234567890  ", "  4321  "])
    @patch("builtins.print")
    def test_main_strips_whitespace(self, mock_print, mock_input):
        """CLI should strip whitespace from input."""
        main()
        mock_print.assert_called_once_with("ACCOUNT VERIFIED")
