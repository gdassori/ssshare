import uuid
from ssshare.domain.user import ShareSessionUser


class ShareSessionMaster(ShareSessionUser):
    ROLE='master'

    @classmethod
    def new(cls, alias=None):
        i = cls(user_id=str(uuid.uuid4()), alias=alias)
        return i

    @property
    def uuid(self):
        return self._uuid

    @property
    def alias(self):
        return self._alias

    def to_dict(self) -> dict:
        return dict(
            uuid=str(self._uuid),
            alias=self._alias
        )