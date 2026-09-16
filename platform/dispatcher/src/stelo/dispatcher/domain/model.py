import dataclasses
import typing as tp
from datetime import datetime

Channel = tp.Literal["sms", "email", "whatsapp"]


@dataclasses.dataclass
class Message:
    """
    dispatcher's own send-outcome record — its row in `dispatcher.messages`.
    Distinct from `stelo.base.messages.Message`, the wire-format
    `TypedDict` this module consumes from `dispatch-in`.
    """

    id: str
    channel: Channel
    recipient: str
    send_status: str
    sent_at: datetime
