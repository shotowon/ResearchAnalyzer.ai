import os
import logging

from pgpt_python.client import PrivateGPTApi
from miniopy_async import Minio

from src.gears.db import DB
from src.gears.logging.logging import setup_logger
from src.config import config
from src.storage.postgres.user_acct_storage import UserAcctStorage
from src.storage.postgres.auth_token_storage import AuthTokenStorage
from src.storage.postgres.file_mapping_storage import MappingStorage
from src.services.user_accts import UserAcctService
from src.services.auth_mailing import MailService as AuthMailService


config_path = os.getenv("RAI_CFG")
if config_path is None:
    config_path = "config/config.yaml"

cfg = config.load(config_path)
setup_logger(cfg.env)

logger = logging.getLogger("rai")

db = DB(dsn=cfg.postgres.dsn, echo=False)
minio = Minio(
    endpoint=cfg.minio.dsn,
    access_key=cfg.minio.access_key,
    secret_key=cfg.minio.secret_key,
    secure=cfg.minio.secure,
)


token_storage = AuthTokenStorage(db=db)
user_storage = UserAcctStorage(db=db)
mapping_storage = MappingStorage(db=db)

user_acct_service = UserAcctService(
    user_storage=user_storage,
    token_storage=token_storage,
    config=cfg.auth,
)

auth_mail_service = AuthMailService(config=cfg.auth_mailer)

summary_store = {}
pgpt_client = PrivateGPTApi(base_url=cfg.pgpt.url)
