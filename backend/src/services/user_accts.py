from dataclasses import dataclass
from datetime import datetime, timezone

from uuid import UUID
import bcrypt
import jwt

import src.storage.auth_token_storage as token_storage
import src.storage.user_acct_storage as user_storage
import src.storage.user_acct_models as user_storage_models
import src.storage.auth_token_models as token_storage_models
from src.config.config import AuthSettings


@dataclass
class RegisterResult:
    id: int


@dataclass
class LoginResult:
    token_id: int
    token: str


@dataclass
class ActivateResult:
    user_id: int


class ErrInternal(Exception):
    pass


class ErrUsernameTaken(Exception):
    pass


class ErrEmailTaken(Exception):
    pass


class ErrInvalidCredentials(Exception):
    pass


class ErrAlreadyActivated(Exception):
    pass


class ErrSessionExpired(Exception):
    pass


class ErrNotFound(Exception):
    pass


class UserAcctService:
    def __init__(
        self,
        user_storage: user_storage.UserAcctStorage,
        token_storage: token_storage.AuthTokenStorage,
        config: AuthSettings,
    ):
        self.__user_storage = user_storage
        self.__token_storage = token_storage
        self.__config = config

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        activation_id: UUID,
    ) -> RegisterResult:
        if await self.__user_storage.username_exists(username):
            raise ErrUsernameTaken
        if await self.__user_storage.email_exists(email):
            raise ErrEmailTaken

        try:
            encrypted_hex_password = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()
            ).hex()

            result = await self.__user_storage.create(
                user_storage_models.CreateBody(
                    username=username,
                    email=email,
                    password=encrypted_hex_password,
                    activation_id=activation_id,
                )
            )

            return RegisterResult(id=result.id)
        except user_storage.ErrInternal as e:
            print(e)
            raise ErrInternal("user-service: register: {}".format(str(e)))
        except Exception as e:
            print(e)
            raise ErrInternal("user-service: register: internal: {}".format(str(e)))

    async def username_login(self, username: str, password: str) -> LoginResult:
        try:
            user = await self.__user_storage.get_by_username(username=username)
        except user_storage.ErrNotFound as e:
            raise ErrInternal(
                "user-service: login: user-storage: not found {}".format(str(e))
            )
        except user_storage.ErrInternal as e:
            raise ErrInternal(
                "user-service: login: user-storage: internal: {}".format(str(e))
            )

        if not bcrypt.checkpw(password.encode(), bytes.fromhex(user.password)):
            raise ErrInvalidCredentials("user-service: login: invalid credentials")

        try:
            token = ""
            while token == "" or await self.__token_storage.token_exists(token):
                expiry = datetime.now(timezone.utc) + self.__config.expiry
                token = jwt.encode(
                    payload={
                        "username": user.username,
                        "user_id": user.id,
                        "exp": expiry,
                    },
                    key=self.__config.secret,
                    algorithm="HS256",
                )

            result = await self.__token_storage.create(
                token_storage_models.CreateBody(
                    user_id=user.id,
                    token=token,
                )
            )
            return LoginResult(token_id=result.id, token=token)
        except token_storage.ErrInternal as e:
            raise ErrInternal("user-service: login: token-storage: {}".format(str(e)))
        except Exception as e:
            raise ErrInternal("user-service: login: internal: {}".format(str(e)))

    async def email_login(self, email: str, password: str) -> LoginResult:
        try:
            user = await self.__user_storage.get_by_email(email=email)
        except user_storage.ErrNotFound as e:
            raise ErrInternal("user-service: email-login: not found {}".format(str(e)))
        except user_storage.ErrInternal as e:
            raise ErrInternal("user-service: email-login: internal: {}".format(str(e)))

        if not bcrypt.checkpw(password.encode(), bytes.fromhex(user.password)):
            raise ErrInvalidCredentials(
                "user-service: email-login: invalid credentials"
            )

        try:
            token = ""
            while token == "" or await self.__token_storage.token_exists(token):
                expiry = datetime.now(timezone.utc) + self.__config.expiry
                token = jwt.encode(
                    payload={
                        "username": user.username,
                        "user_id": user.id,
                        "exp": expiry,
                    },
                    key=self.__config.secret,
                    algorithm="HS256",
                )

            result = await self.__token_storage.create(
                token_storage_models.CreateBody(
                    user_id=user.id,
                    token=token,
                )
            )

            return LoginResult(token_id=result.id, token=token)
        except token_storage.ErrInternal as e:
            raise ErrInternal("user-service: login: token-storage: {}".format(str(e)))
        except Exception as e:
            raise ErrInternal("user-service: login: internal: {}".format(str(e)))

    async def logout(self, token: str) -> None:
        try:
            await self.__token_storage.delete_token(token=token)
        except token_storage.ErrNotFound as e:
            raise ErrNotFound("user-service: logout: not-found: {}".format(str(e)))
        except Exception as e:
            raise ErrInternal("user-service: logout: internal: {}")

    async def verify(self, token: str) -> bool:
        try:
            token_from_db = await self.__token_storage.get_by_token(token)
            try:
                result = jwt.decode(token, self.__config.secret, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                await self.logout(token=token)
                return False
        except token_storage.ErrNotFound:
            raise ErrNotFound("user-service: verify: not-found")
        except Exception as e:
            raise ErrInternal("user-service: verify: internal: {}".format(str(e)))

        return True

    async def activate(self, activation_id: UUID) -> ActivateResult:
        try:
            result = await self.__user_storage.activate(activation_id=activation_id)
        except user_storage.ErrAlreadyActivated as e:
            raise ErrAlreadyActivated(
                "user-service: activate: already-activated: {}".format(str(e))
            )
        except user_storage.ErrNotFound as e:
            raise ErrNotFound(
                "user-service: activate: there's no user with activation_id = {}".format(
                    str(activation_id)
                )
            )
        except Exception as e:
            raise ErrInternal("user-service: activate: internal: {}".format(str(e)))
        return ActivateResult(user_id=result.user_id)
