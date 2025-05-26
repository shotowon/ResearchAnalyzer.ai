from email.message import EmailMessage
import ssl

import aiosmtplib

from src.config.config import AuthMailerSettings


class MailService:
    def __init__(self, config: AuthMailerSettings):
        self.__cfg = config

    async def send_activation_request(
        self,
        dst_email: str,
        username: str,
        activation_id: str,
    ) -> None:
        message = EmailMessage()
        message["From"] = self.__cfg.from_address
        message["To"] = dst_email
        message["Subject"] = "Activate ResearchAnalyzer.ai account."
        message.set_content(
            self.__build_activation_request_message(
                username=username,
                activation_id=activation_id,
            )
        )

        if not self.__cfg.tls_verification:
            ssl_ctx = ssl._create_unverified_context()

            await aiosmtplib.send(
                message,
                hostname=self.__cfg.smtp_host,
                port=self.__cfg.smtp_port,
                use_tls=self.__cfg.use_tls,
                tls_context=ssl_ctx,
                sender=self.__cfg.from_address,
                username=self.__cfg.username,
                password=self.__cfg.password,
            )
            return

        await aiosmtplib.send(
            message,
            hostname=self.__cfg.smtp_host,
            port=self.__cfg.smtp_port,
            use_tls=self.__cfg.use_tls,
            tls_context=ssl_ctx,
            sender=self.__cfg.from_address,
            username=self.__cfg.username,
            password=self.__cfg.password,
        )

    def __build_activation_request_message(
        self, username: str, activation_id: str
    ) -> str:
        return """Dear {} we glad you joined ResearchAnalyzer.ai, please click provided link, to activate your account. Link: {}""".format(
            username,
            "{}/{}".format(self.__cfg.activation_endpoint, activation_id),
        )
