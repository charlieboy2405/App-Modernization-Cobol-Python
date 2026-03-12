"""
Comprehensive tests for the account verification module.

Covers all verification paths from the original COBOL VERIFY-ACCOUNT logic:
1. Account not found (account number mismatch)
2. Account not active (correct account, inactive status)
3. Account verified (correct account, active, correct PIN)
4. Invalid PIN (correct account, active, wrong PIN)

Also tests edge cases, the AccountRecord dataclass, the CLI entry point,
and the module's public API.
"""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from account_verify.account_verify import (
    DEFAULT_ACCOUNT,
    AccountRecord,
    verify_account,
)
from account_verify.main import main


# ---------------------------------------------------------------------------
# AccountRecord dataclass tests
# ---------------------------------------------------------------------------


class TestAccountRecord:
    """Tests for the AccountRecord dataclass."""

    def test_create_record(self) -> None:
        record = AccountRecord(account_no="1111111111", pin="0000", status="ACTIVE")
        assert record.account_no == "1111111111"
        assert record.pin == "0000"
        assert record.status == "ACTIVE"

    def test_default_account_values(self) -> None:
        """Verify DEFAULT_ACCOUNT matches the original COBOL hardcoded values."""
        assert DEFAULT_ACCOUNT.account_no == "1234567890"
        assert DEFAULT_ACCOUNT.pin == "4321"
        assert DEFAULT_ACCOUNT.status == "ACTIVE"

    def test_equality(self) -> None:
        a = AccountRecord(account_no="A", pin="1", status="ACTIVE")
        b = AccountRecord(account_no="A", pin="1", status="ACTIVE")
        assert a == b

    def test_inequality(self) -> None:
        a = AccountRecord(account_no="A", pin="1", status="ACTIVE")
        b = AccountRecord(account_no="B", pin="1", status="ACTIVE")
        assert a != b


# ---------------------------------------------------------------------------
# Core verification logic tests (mirrors COBOL VERIFY-ACCOUNT paragraph)
# ---------------------------------------------------------------------------


class TestVerifyAccount:
    """Tests for the verify_account function using the default account."""

    def test_account_verified(self) -> None:
        """Correct account number and correct PIN → ACCOUNT VERIFIED."""
        result = verify_account("1234567890", "4321")
        assert result == "ACCOUNT VERIFIED"

    def test_account_not_found_wrong_number(self) -> None:
        """Wrong account number → ACCOUNT NOT FOUND."""
        result = verify_account("0000000000", "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_account_not_found_empty(self) -> None:
        """Empty account number → ACCOUNT NOT FOUND."""
        result = verify_account("", "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_invalid_pin(self) -> None:
        """Correct account, active, wrong PIN → INVALID PIN."""
        result = verify_account("1234567890", "9999")
        assert result == "INVALID PIN"

    def test_invalid_pin_empty(self) -> None:
        """Correct account, active, empty PIN → INVALID PIN."""
        result = verify_account("1234567890", "")
        assert result == "INVALID PIN"


class TestVerifyAccountCustomRecord:
    """Tests with custom AccountRecord instances to cover all branches."""

    def test_account_not_active(self) -> None:
        """Account found but status is not ACTIVE → ACCOUNT NOT ACTIVE."""
        inactive = AccountRecord(
            account_no="AAAAAAAAAA", pin="1111", status="CLOSED"
        )
        result = verify_account("AAAAAAAAAA", "1111", stored_account=inactive)
        assert result == "ACCOUNT NOT ACTIVE"

    def test_account_not_active_suspended(self) -> None:
        """Account with SUSPENDED status → ACCOUNT NOT ACTIVE."""
        suspended = AccountRecord(
            account_no="BBBBBBBBBB", pin="2222", status="SUSPENDED"
        )
        result = verify_account("BBBBBBBBBB", "2222", stored_account=suspended)
        assert result == "ACCOUNT NOT ACTIVE"

    def test_account_not_active_empty_status(self) -> None:
        """Account with empty status → ACCOUNT NOT ACTIVE."""
        empty_status = AccountRecord(
            account_no="CCCCCCCCCC", pin="3333", status=""
        )
        result = verify_account("CCCCCCCCCC", "3333", stored_account=empty_status)
        assert result == "ACCOUNT NOT ACTIVE"

    def test_account_not_found_takes_priority(self) -> None:
        """Wrong account number returns NOT FOUND even if status is inactive."""
        inactive = AccountRecord(
            account_no="AAAAAAAAAA", pin="1111", status="CLOSED"
        )
        result = verify_account("WRONG", "1111", stored_account=inactive)
        assert result == "ACCOUNT NOT FOUND"

    def test_verified_custom_record(self) -> None:
        """Custom active account with correct PIN → ACCOUNT VERIFIED."""
        record = AccountRecord(
            account_no="CUSTOMACCT", pin="5678", status="ACTIVE"
        )
        result = verify_account("CUSTOMACCT", "5678", stored_account=record)
        assert result == "ACCOUNT VERIFIED"

    def test_invalid_pin_custom_record(self) -> None:
        """Custom active account with wrong PIN → INVALID PIN."""
        record = AccountRecord(
            account_no="CUSTOMACCT", pin="5678", status="ACTIVE"
        )
        result = verify_account("CUSTOMACCT", "0000", stored_account=record)
        assert result == "INVALID PIN"


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_whitespace_account_no(self) -> None:
        """Whitespace-only account number does not match default account."""
        result = verify_account("          ", "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_partial_account_no(self) -> None:
        """Partial account number does not match."""
        result = verify_account("12345", "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_account_no_with_trailing_space(self) -> None:
        """Account number with trailing space does not match (exact match)."""
        result = verify_account("1234567890 ", "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_pin_with_leading_space(self) -> None:
        """PIN with leading space does not match stored PIN."""
        result = verify_account("1234567890", " 4321")
        assert result == "INVALID PIN"

    def test_case_sensitive_status(self) -> None:
        """Status comparison is case-sensitive (mirroring COBOL behavior)."""
        lower_active = AccountRecord(
            account_no="DDDDDDDDDD", pin="4444", status="active"
        )
        result = verify_account("DDDDDDDDDD", "4444", stored_account=lower_active)
        assert result == "ACCOUNT NOT ACTIVE"

    def test_very_long_account_no(self) -> None:
        """Very long account number does not match."""
        result = verify_account("A" * 100, "4321")
        assert result == "ACCOUNT NOT FOUND"

    def test_special_characters_in_account(self) -> None:
        """Special characters in account number - still exact match logic."""
        record = AccountRecord(account_no="!@#$%^&*()", pin="1234", status="ACTIVE")
        result = verify_account("!@#$%^&*()", "1234", stored_account=record)
        assert result == "ACCOUNT VERIFIED"


# ---------------------------------------------------------------------------
# CLI (main) tests
# ---------------------------------------------------------------------------


class TestMainCLI:
    """Tests for the CLI entry point in main.py."""

    def test_main_account_verified(self) -> None:
        """CLI prints ACCOUNT VERIFIED for correct credentials."""
        with patch("builtins.input", side_effect=["1234567890", "4321"]):
            captured = StringIO()
            sys.stdout = captured
            main()
            sys.stdout = sys.__stdout__
            assert captured.getvalue().strip() == "ACCOUNT VERIFIED"

    def test_main_account_not_found(self) -> None:
        """CLI prints ACCOUNT NOT FOUND for wrong account."""
        with patch("builtins.input", side_effect=["0000000000", "4321"]):
            captured = StringIO()
            sys.stdout = captured
            main()
            sys.stdout = sys.__stdout__
            assert captured.getvalue().strip() == "ACCOUNT NOT FOUND"

    def test_main_invalid_pin(self) -> None:
        """CLI prints INVALID PIN for wrong PIN."""
        with patch("builtins.input", side_effect=["1234567890", "0000"]):
            captured = StringIO()
            sys.stdout = captured
            main()
            sys.stdout = sys.__stdout__
            assert captured.getvalue().strip() == "INVALID PIN"

    def test_main_eof_exits(self) -> None:
        """CLI exits gracefully on EOF (e.g., piped empty input)."""
        with patch("builtins.input", side_effect=EOFError):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_keyboard_interrupt_exits(self) -> None:
        """CLI exits gracefully on Ctrl+C."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Module public API tests
# ---------------------------------------------------------------------------


class TestModuleAPI:
    """Verify the package exposes the expected public API."""

    def test_import_from_package(self) -> None:
        from account_verify import AccountRecord, verify_account

        assert callable(verify_account)
        assert AccountRecord is not None

    def test_default_account_accessible(self) -> None:
        from account_verify.account_verify import DEFAULT_ACCOUNT

        assert isinstance(DEFAULT_ACCOUNT, AccountRecord)
