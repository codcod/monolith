import logging

import pytest

from stelo.base import channels


def test_senders_registered_for_every_channel():
    assert set(channels.SENDERS) == {'sms', 'email', 'whatsapp'}
    assert isinstance(channels.SENDERS['sms'], channels.SmsSender)
    assert isinstance(channels.SENDERS['email'], channels.EmailSender)
    assert isinstance(channels.SENDERS['whatsapp'], channels.WhatsAppSender)


@pytest.mark.parametrize(
    'sender_cls, label',
    [
        (channels.SmsSender, 'SMS'),
        (channels.EmailSender, 'email'),
        (channels.WhatsAppSender, 'WhatsApp'),
    ],
)
async def test_sender_logs_the_send(sender_cls, label, caplog):
    with caplog.at_level(logging.INFO):
        await sender_cls().send('+1', 'hi')
    assert any(label in r.message for r in caplog.records)
