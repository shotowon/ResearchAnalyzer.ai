from datetime import timedelta
from typing import Literal
from pathlib import Path
import os

from pydantic_settings import BaseSettings
import yaml


class AppSettings(BaseSettings):
    env: Literal["local", "dev", "prod"]
    cors: "CORSSettings"
    http_server: "HTTPServerSettings"
    auth: "AuthSettings"
    postgres: "PostgresSettings"
    pgpt: "PGPTSettings"
    auth_mailer: "AuthMailerSettings"
    minio: "MinioSettings"


def load(filepath: str) -> "AppSettings":
    path = Path(filepath)

    with open(path) as file:
        config_dict = yaml.safe_load(file)
    config = AppSettings(**config_dict)
    return config


class CORSSettings(BaseSettings):
    frontend_url: str


class HTTPServerSettings(BaseSettings):
    host: str
    port: int


class AuthSettings(BaseSettings):
    secret: str
    expiry: timedelta


class PostgresSettings(BaseSettings):
    dsn: str


class PGPTSettings(BaseSettings):
    url: str


class AuthMailerSettings(BaseSettings):
    smtp_host: str
    smtp_port: int
    tls_verification: bool
    activation_endpoint: str
    use_tls: bool
    from_address: str
    username: str
    password: str


class MinioSettings(BaseSettings):
    dsn: str
    access_key: str
    secret_key: str
    secure: bool
