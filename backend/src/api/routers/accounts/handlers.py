from typing import Annotated

from fastapi import APIRouter, Header, Depends, status
from fastapi.responses import JSONResponse
import uuid

from src.services.user_accts import UserAcctService
from src.services.auth_mailing import MailService as AuthMailService
from src.api.validators import emails
from src.services import user_accts
from src.init import logger as rootLogger

from ..dependencies import get_user_service, get_auth_mail_service
from .schemas import (
    RegisterSchema,
    RegisterResponse,
    LoginSchema,
    LoginResponse,
    ActivateResponse,
    LogoutResponse,
    VerifyResponse,
)


router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(
    user: RegisterSchema,
    user_service: Annotated[UserAcctService, Depends(get_user_service)],
    auth_mail_serivce: Annotated[AuthMailService, Depends(get_auth_mail_service)],
):
    try:
        logger = rootLogger.getChild("user-accounts.register")
        activation_id = uuid.uuid4()

        result = await user_service.register(
            username=user.username,
            email=user.email,
            password=user.password,
            activation_id=activation_id,
        )

        try:
            await auth_mail_serivce.send_activation_request(
                dst_email=user.email,
                username=user.username,
                activation_id=activation_id,
            )
        except Exception as e:
            logger.error(
                "failed to send activation request to user: username = {}; email = {};".format(
                    user.username, user.email
                )
            )

        return RegisterResponse(message="User was registered", user_id=result.id)
    except user_accts.ErrUsernameTaken:
        logger.error("".format(user.username, user.email))
        return JSONResponse(
            {"message": "user with username '{}' already exists".format(user.username)},
            status_code=status.HTTP_409_CONFLICT,
        )
    except user_accts.ErrEmailTaken:
        return JSONResponse(
            {"message": "user with email '{}' already exists".format(user.email)},
            status_code=status.HTTP_409_CONFLICT,
        )
    except user_accts.ErrInternal as e:
        print(e)
        return JSONResponse(
            {"message": "internal_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            {"message": "internal_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login: LoginSchema,
    user_service: Annotated[UserAcctService, Depends(get_user_service)],
):
    logger = rootLogger.getChild("user-accounts.login")
    try:
        if emails.is_email(login.login):
            result = await user_service.email_login(
                email=login.login, password=login.password
            )
        else:
            result = await user_service.username_login(
                username=login.login, password=login.password
            )

        return LoginResponse(token=result.token)
    except user_accts.ErrInvalidCredentials as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "invalid login or password"},
        )
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "internal error"},
        )


@router.get("/verify", response_model=VerifyResponse)
async def verify(
    authorization: Annotated[str | None, Header()],
    user_service: Annotated[UserAcctService, Depends(get_user_service)],
):
    logger = rootLogger.getChild("user-accounts.verify")
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "You must be authorized to logout."},
        )

    token = authorization.removeprefix("Bearer ")
    try:
        result = await user_service.verify(token=token)
        if not result:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "token expired"},
            )
    except user_accts.ErrNotFound as e:
        logger.error(
            "user is trying to verify token that doesn't exist: token = %s", token
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "session doesn't exist"},
        )
    except Exception as e:
        logger.error("failed to verify token = %s", token)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "internal error"},
        )
    return VerifyResponse(message="token is up to date.")


@router.delete("/logout", response_model=LogoutResponse)
async def logout(
    authorization: Annotated[str | None, Header()],
    user_service: Annotated[UserAcctService, Depends(get_user_service)],
):
    logger = rootLogger.getChild("user-accounts.logout")
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "You must be authorized to logout."},
        )

    token = authorization.removeprefix("Bearer ")
    try:
        await user_service.logout(token)
    except user_accts.ErrNotFound:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "expired session, you can login again"},
        )
    except Exception as e:
        logger.error("internal error %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "internal error"},
        )

    return LogoutResponse(message="session is deleted")


@router.get("/activate/{activation_id}", response_model=ActivateResponse)
async def activate(
    activation_id: str,
    user_service: Annotated[UserAcctService, Depends(get_user_service)],
):
    try:
        result = await user_service.activate(uuid.UUID(activation_id))
    except user_accts.ErrNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "resource not found"},
        )
    except user_accts.ErrAlreadyActivated as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "resource not found"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "resource not found"},
        )
    return ActivateResponse(
        user_id=result.user_id,
        message="Your account was activated.",
    )
