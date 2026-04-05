"""Simple token-based authentication."""

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import settings

security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> str:
    """Verify the bearer token. Returns the token if valid."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    if credentials.credentials != settings.AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid authorization token")

    return credentials.credentials
