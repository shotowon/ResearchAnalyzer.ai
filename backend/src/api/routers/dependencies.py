from typing import Annotated
import jwt

from fastapi import Depends, HTTPException, Header, status
from src.services.user_accts import UserAcctService
from src.services.auth_mailing import MailService as AuthMailService
from src.services.documents import DocumentService
from src.init import user_acct_service, auth_mail_service, document_service, cfg


def get_user_service() -> UserAcctService:
    return user_acct_service


def get_auth_mail_service() -> AuthMailService:
    return auth_mail_service


def get_document_service() -> DocumentService:
    return document_service


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    user_service: Annotated[UserAcctService, Depends(get_user_service)] = None,
) -> dict:
    """
    Get the current authenticated user from the JWT token.
    Raises HTTPException if token is invalid or missing.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ")

    try:
        # Verify token exists in database
        is_valid = await user_service.verify(token=token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode JWT token
        payload = jwt.decode(token, cfg.auth.secret, algorithms=["HS256"])
        return {
            "id": payload["user_id"],
            "username": payload["username"]
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
