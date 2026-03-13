"""Tests for data models - validates COBOL WORKING-STORAGE data structure conversions."""

from app.models import (
    AccountInput,
    AccountRecord,
    AccountStatus,
    VerificationMessage,
    VerificationResult,
)


class TestAccountStatus:
    """Tests for AccountStatus enum."""

    def test_active_status(self) -> None:
        assert AccountStatus.ACTIVE.value == "ACTIVE"

    def test_inactive_status(self) -> None:
        assert AccountStatus.INACTIVE.value == "INACTIVE"

    def test_suspended_status(self) -> None:
        assert AccountStatus.SUSPENDED.value == "SUSPENDED"


class TestVerificationMessage:
    """Tests for VerificationMessage enum - matches COBOL WS-RESULT values."""

    def test_account_verified(self) -> None:
        assert VerificationMessage.ACCOUNT_VERIFIED.value == "ACCOUNT VERIFIED"

    def test_account_not_found(self) -> None:
        assert VerificationMessage.ACCOUNT_NOT_FOUND.value == "ACCOUNT NOT FOUND"

    def test_account_not_active(self) -> None:
        assert VerificationMessage.ACCOUNT_NOT_ACTIVE.value == "ACCOUNT NOT ACTIVE"

    def test_invalid_pin(self) -> None:
        assert VerificationMessage.INVALID_PIN.value == "INVALID PIN"


class TestAccountInput:
    """Tests for AccountInput - corresponds to COBOL WS-INPUT group."""

    def test_create_input(self) -> None:
        inp = AccountInput(account_no="1234567890", pin="4321")
        assert inp.account_no == "1234567890"
        assert inp.pin == "4321"

    def test_empty_values(self) -> None:
        inp = AccountInput(account_no="", pin="")
        assert inp.account_no == ""
        assert inp.pin == ""

    def test_max_length_account_no(self) -> None:
        """COBOL PIC X(10) allows up to 10 characters."""
        inp = AccountInput(account_no="1234567890", pin="4321")
        assert len(inp.account_no) == 10

    def test_max_length_pin(self) -> None:
        """COBOL PIC X(4) allows up to 4 characters."""
        inp = AccountInput(account_no="1234567890", pin="4321")
        assert len(inp.pin) == 4


class TestAccountRecord:
    """Tests for AccountRecord - corresponds to COBOL WS-ACCOUNT-RECORD group."""

    def test_default_values_match_cobol(self) -> None:
        """Default values must match COBOL VALUE clauses."""
        record = AccountRecord()
        assert record.stored_account == "1234567890"
        assert record.stored_pin == "4321"
        assert record.status == AccountStatus.ACTIVE

    def test_custom_values(self) -> None:
        record = AccountRecord(
            stored_account="9876543210",
            stored_pin="1234",
            status=AccountStatus.INACTIVE,
        )
        assert record.stored_account == "9876543210"
        assert record.stored_pin == "1234"
        assert record.status == AccountStatus.INACTIVE


class TestVerificationResult:
    """Tests for VerificationResult - corresponds to COBOL WS-RESULT."""

    def test_success_result(self) -> None:
        result = VerificationResult(
            message=VerificationMessage.ACCOUNT_VERIFIED,
            success=True,
        )
        assert result.message == VerificationMessage.ACCOUNT_VERIFIED
        assert result.success is True
        assert result.result_text == "ACCOUNT VERIFIED"

    def test_failure_result(self) -> None:
        result = VerificationResult(
            message=VerificationMessage.ACCOUNT_NOT_FOUND,
            success=False,
        )
        assert result.message == VerificationMessage.ACCOUNT_NOT_FOUND
        assert result.success is False
        assert result.result_text == "ACCOUNT NOT FOUND"

    def test_result_text_property(self) -> None:
        """result_text should return the enum value string."""
        for msg in VerificationMessage:
            result = VerificationResult(message=msg, success=False)
            assert result.result_text == msg.value
