import logging
import typing as tp

logger = logging.getLogger(__name__)


class Sender(tp.Protocol):
    async def send(self, recipient: str, body: str) -> None: ...


class SmsSender:
    async def send(self, recipient: str, body: str) -> None:
        logger.info('would send SMS to %s: %s', recipient, body)


class EmailSender:
    async def send(self, recipient: str, body: str) -> None:
        logger.info('would send email to %s: %s', recipient, body)


class WhatsAppSender:
    async def send(self, recipient: str, body: str) -> None:
        logger.info('would send WhatsApp to %s: %s', recipient, body)


# Stub senders only — no provider SDKs, no credentials. Swap an entry with a
# real implementation of `Sender` to wire up an actual channel.
SENDERS: dict[str, Sender] = {
    'sms': SmsSender(),
    'email': EmailSender(),
    'whatsapp': WhatsAppSender(),
}
