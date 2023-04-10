from __future__ import annotations

from enum import Enum


class UserRoleEnum(Enum):
    ADMIN = "admin"
    DEV = "dev"
    SUBSCRIBER = "subscriber"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
