import typing as tp

Channel = tp.Literal['sms', 'email', 'whatsapp']
Status = tp.Literal['received', 'routed', 'sent']


class Message(tp.TypedDict):
    """
    The one shared shape that flows through the traffic-in / dispatch-in
    streams. Everything past this (each module's own DB rows) is free to
    differ per module.
    """

    id: str
    channel: Channel
    recipient: str
    body: str
    status: Status
    created_at: str
