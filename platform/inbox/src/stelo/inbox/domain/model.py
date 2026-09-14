import dataclasses
import typing as tp
from datetime import datetime

Channel = tp.Literal['sms', 'email', 'whatsapp']


@dataclasses.dataclass
class Message:
    """
    inbox's own intake record — its row in `inbox.messages`. Distinct from
    `stelo.base.messages.Message`, the wire-format `TypedDict` published to
    the `traffic-in` stream: the two already diverge (`received_at` here vs
    `created_at`/`status` on the wire), and each bounded context is free to
    keep evolving its own shape independently of the wire format.
    """

    id: str
    channel: Channel
    recipient: str
    body: str
    received_at: datetime
