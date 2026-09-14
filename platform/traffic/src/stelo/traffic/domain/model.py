import dataclasses
import typing as tp
from datetime import datetime

Channel = tp.Literal['sms', 'email', 'whatsapp']


@dataclasses.dataclass
class Message:
    """
    traffic's own routing record — its row in `traffic.messages`. Distinct
    from `stelo.base.messages.Message`, the wire-format `TypedDict` this
    module consumes from `traffic-in` and republishes to `dispatch-in`.
    """

    id: str
    channel: Channel
    recipient: str
    routed_at: datetime
