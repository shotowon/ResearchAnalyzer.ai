from src.services.user_accts import UserAcctService
from src.services.auth_mailing import MailService as AuthMailService
from src.init import user_acct_service, auth_mail_service


def get_user_service() -> UserAcctService:
    return user_acct_service


def get_auth_mail_service() -> AuthMailService:
    return auth_mail_service
