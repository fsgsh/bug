from datetime import datetime
from typing import Optional


class BanInfo:
    id: int
    reason: str
    date: datetime
    timestamp: int
    admin: int
    message: Optional[str]

    def __init__(self,
                 id: int,
                 reason: str,
                 admin: int,
                 date: int = 0,
                 message: Optional[str] = None,
                 **kwargs) -> None:
        self.id = id
        self.reason = reason
        self.date = datetime.fromtimestamp(date)
        self.timestamp = date
        self.admin = admin
        self.message = message

    def __str__(self) -> str:
        return f'<{self.__class__.__name__}: {self.__dict__}>'

    def __repr__(self) -> str:
        return self.__str__()
