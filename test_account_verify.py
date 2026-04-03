import pytest
from unittest.mock import patch
from account_verify import AccountVerifier, AccountRecord, main

# --- Fixtures ---


@pytest.fixture
def verifier():
    """Verifier with default hardcoded account (mirrors COBOL defaults)."""
    return AccountVerifier()


@pytest.fixture
def multi_account_verifier():
    """Verifier with multiple accounts including an inactive one."""
    accounts = [
        AccountRecord("1234567890", "4321", "ACTIVE"),
        AccountRecord("0000000001", "1111", "INACTIVE"),
        AccountRecord("9999999999", "9999", "ACTIVE"),
    ]
    return AccountVerifier(accounts)


# --- Core verification tests (mirror COBOL logic) ---


class TestVerifyAccount:
    def test_account_verified(self, verifier):
        """Correct account + ACTIVE status + correct PIN -> ACCOUNT VERIFIED"""
        assert verifier.verify("1234567890", "4321") == "ACCOUNT VERIFIED"

    def test_account_not_found(self, verifier):
        """Unknown account number -> ACCOUNT NOT FOUND"""
        assert verifier.verify("0000000000", "4321") == "ACCOUNT NOT FOUND"

    def test_invalid_pin(self, verifier):
        """Correct account + ACTIVE status + wrong PIN -> INVALID PIN"""
        assert verifier.verify("1234567890", "0000") == "INVALID PIN"

    def test_account_not_active(self, multi_account_verifier):
        """Known account + INACTIVE status -> ACCOUNT NOT ACTIVE"""
        assert multi_account_verifier.verify("0000000001", "1111") == "ACCOUNT NOT ACTIVE"

    def test_account_not_active_even_with_correct_pin(self, multi_account_verifier):
        """Inactive account should fail even if PIN is correct (gate 2 before gate 3)."""
        assert multi_account_verifier.verify("0000000001", "1111") == "ACCOUNT NOT ACTIVE"

    def test_second_active_account_verified(self, multi_account_verifier):
        """Verify a second active account works."""
        assert multi_account_verifier.verify("9999999999", "9999") == "ACCOUNT VERIFIED"


# --- Edge case tests ---


class TestEdgeCases:
    def test_empty_account_number(self, verifier):
        assert verifier.verify("", "4321") == "ACCOUNT NOT FOUND"

    def test_empty_pin(self, verifier):
        assert verifier.verify("1234567890", "") == "INVALID PIN"

    def test_both_empty(self, verifier):
        assert verifier.verify("", "") == "ACCOUNT NOT FOUND"

    def test_partial_account_number(self, verifier):
        assert verifier.verify("12345", "4321") == "ACCOUNT NOT FOUND"

    def test_account_with_extra_chars(self, verifier):
        assert verifier.verify("1234567890X", "4321") == "ACCOUNT NOT FOUND"

    def test_pin_with_extra_chars(self, verifier):
        assert verifier.verify("1234567890", "43210") == "INVALID PIN"

    def test_case_sensitivity_account(self, verifier):
        """Account numbers should be case-sensitive (matching COBOL PIC X behavior)."""
        assert verifier.verify("ABCDEFGHIJ", "4321") == "ACCOUNT NOT FOUND"

    def test_no_accounts(self):
        """Verifier with empty account list."""
        verifier = AccountVerifier(accounts=[])
        assert verifier.verify("1234567890", "4321") == "ACCOUNT NOT FOUND"


# --- Console I/O tests ---


class TestMainFunction:
    @patch("builtins.input", side_effect=["1234567890", "4321"])
    @patch("builtins.print")
    def test_main_verified(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("ACCOUNT VERIFIED")

    @patch("builtins.input", side_effect=["0000000000", "4321"])
    @patch("builtins.print")
    def test_main_not_found(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("ACCOUNT NOT FOUND")

    @patch("builtins.input", side_effect=["1234567890", "0000"])
    @patch("builtins.print")
    def test_main_invalid_pin(self, mock_print, mock_input):
        main()
        mock_print.assert_called_once_with("INVALID PIN")


# --- AccountRecord tests ---


class TestAccountRecord:
    def test_record_attributes(self):
        rec = AccountRecord("ACC123", "9999", "ACTIVE")
        assert rec.account_no == "ACC123"
        assert rec.pin == "9999"
        assert rec.status == "ACTIVE"
