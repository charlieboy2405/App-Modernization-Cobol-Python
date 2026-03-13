"""FastAPI web service for Account Verification.

Modern REST API wrapper around the converted COBOL ACCOUNT-VERIFY logic.
Provides HTTP endpoints for account verification, replacing the terminal-based
COBOL ACCEPT/DISPLAY I/O with JSON request/response patterns.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.account_verify import verify_account
from app.models import AccountInput

app = FastAPI(
    title="Account Verification Service",
    description=(
        "Python conversion of COBOL ACCOUNT-VERIFY program. "
        "Provides REST API endpoints for account number and PIN verification."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    """Request body for account verification.

    Maps to COBOL WS-INPUT:
      05 WS-ACCOUNT-NO PIC X(10) -> account_no (max 10 characters)
      05 WS-PIN         PIC X(4) -> pin (max 4 characters)
    """

    account_no: str = Field(
        ...,
        max_length=10,
        description="Account number (COBOL WS-ACCOUNT-NO, PIC X(10))",
        examples=["1234567890"],
    )
    pin: str = Field(
        ...,
        max_length=4,
        description="Personal Identification Number (COBOL WS-PIN, PIC X(4))",
        examples=["4321"],
    )


class VerifyResponse(BaseModel):
    """Response body for account verification.

    Maps to COBOL WS-RESULT PIC X(30).
    """

    result: str = Field(
        ...,
        description="Verification result message (COBOL WS-RESULT)",
    )
    success: bool = Field(
        ...,
        description="Whether the verification was successful",
    )


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest) -> VerifyResponse:
    """Verify account credentials.

    Converts the COBOL MAIN-PARA flow into a single API call:
    - Receives account_no and pin (replaces ACCEPT statements)
    - Calls verify_account (replaces PERFORM VERIFY-ACCOUNT)
    - Returns the result (replaces DISPLAY WS-RESULT)
    """
    account_input = AccountInput(
        account_no=request.account_no,
        pin=request.pin,
    )
    verification_result = verify_account(account_input)

    return VerifyResponse(
        result=verification_result.result_text,
        success=verification_result.success,
    )
