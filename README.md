# Account Verification — COBOL to Python Conversion

This project converts the legacy COBOL program `ACCOUNT-VERIFY` (documented in
`Financial-Investment-Unit-Trust-COBOL-code-12th-Mar-2026.md`) into a
well-structured, production-ready Python module with comprehensive tests.

## What It Does

The `account_verify` module performs three-tier account verification mirroring
the original COBOL logic:

1. **Account existence** — checks whether the supplied account number matches a
   known record.
2. **Account status** — confirms the account is `ACTIVE`.
3. **PIN authentication** — validates the entered PIN against the stored value.

### Verification Outcomes

| Result               | Meaning                                      |
|----------------------|----------------------------------------------|
| `ACCOUNT VERIFIED`   | Account found, active, and PIN matches       |
| `ACCOUNT NOT FOUND`  | No record with the given account number      |
| `ACCOUNT NOT ACTIVE` | Account exists but is not in ACTIVE status   |
| `INVALID PIN`        | Account is active but the PIN does not match |

## Quick Start

### Prerequisites

- Python 3.10+
- `pytest` (install via `pip install -r requirements.txt`)

### Run the Program

```bash
python account_verify.py
```

You will be prompted to enter an account number and PIN. The default hardcoded
account mirrors the original COBOL values:

- **Account number:** `1234567890`
- **PIN:** `4321`

### Run the Tests

```bash
pytest test_account_verify.py -v
```

## Project Structure

| File                        | Description                                 |
|-----------------------------|---------------------------------------------|
| `account_verify.py`         | Core verification module and CLI entry point|
| `test_account_verify.py`    | Comprehensive pytest test suite             |
| `requirements.txt`          | Python dependencies                         |
| `Financial-Investment-Unit-Trust-COBOL-code-12th-Mar-2026.md` | Original COBOL source |

## Extending with a Real Database

The `AccountVerifier` class accepts an injectable list of `AccountRecord`
objects. To integrate with a real database:

1. Query your database for account records.
2. Map each row to an `AccountRecord(account_no, pin, status)` instance.
3. Pass the list to `AccountVerifier(accounts=my_records)`.

```python
from account_verify import AccountVerifier, AccountRecord

# Example: load from a database query result
records = [AccountRecord(row["acct"], row["pin"], row["status"]) for row in db_rows]
verifier = AccountVerifier(accounts=records)
result = verifier.verify(user_account, user_pin)
```
