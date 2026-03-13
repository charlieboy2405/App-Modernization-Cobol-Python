"""Tests for CLI interface - validates COBOL MAIN-PARA conversion."""

from unittest.mock import patch

from app.cli import main


class TestCLI:
    """Tests for the CLI entry point matching COBOL MAIN-PARA."""

    def test_successful_verification(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test CLI with valid credentials."""
        with patch("builtins.input", side_effect=["1234567890", "4321"]):
            main()
        captured = capsys.readouterr()
        assert captured.out.strip() == "ACCOUNT VERIFIED"

    def test_account_not_found(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test CLI with wrong account number."""
        with patch("builtins.input", side_effect=["0000000000", "4321"]):
            main()
        captured = capsys.readouterr()
        assert captured.out.strip() == "ACCOUNT NOT FOUND"

    def test_invalid_pin(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test CLI with wrong PIN."""
        with patch("builtins.input", side_effect=["1234567890", "0000"]):
            main()
        captured = capsys.readouterr()
        assert captured.out.strip() == "INVALID PIN"

    def test_prompts_match_cobol(self) -> None:
        """Verify input prompts match COBOL DISPLAY statements."""
        calls = []
        with patch("builtins.input", side_effect=["1234567890", "4321"]) as mock_input:
            main()
            calls = [call.args[0] for call in mock_input.call_args_list]
        assert calls[0] == "ENTER ACCOUNT NUMBER: "
        assert calls[1] == "ENTER PIN: "
