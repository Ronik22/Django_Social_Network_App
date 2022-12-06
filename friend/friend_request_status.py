from enum import Enum


class FriendRequestStatus(Enum):
    NO_REQUEST_SENT: int = -1
    THEM_SENT_TO_YOU: int = 0
    YOU_SENT_TO_THEM: int = 1
