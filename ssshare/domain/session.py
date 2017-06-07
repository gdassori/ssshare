import time
from uuid import UUID

from ssshare import exceptions, settings
from ssshare.domain import DomainObject
from ssshare.domain.master import ShareSessionMaster
from ssshare.ioc import secret_share_repository


class ShareSession(DomainObject):
    def __init__(self, master: ShareSessionMaster=None, alias=None, repo=secret_share_repository):
        self._repo = repo
        self._master = master
        self._uuid = None
        self._users = {}
        self._secret = None
        self._alias = alias
        self._last_update = None
        self._session_ttl = settings.SESSION_TTL

    @classmethod
    def new(cls, master=None, alias=None, repo=secret_share_repository):
        i = cls(master=master, alias=alias, repo=repo)
        return i

    @property
    def master(self):
        return self._master

    @property
    def ttl(self):
        if not self._last_update:
            raise exceptions.SystemException('the object must be stored first')
        rem = self._session_ttl - (int(time.time()) - self._last_update)
        return self._session_ttl if self._session_ttl == -1 else rem > 0 and rem or 0

    @classmethod
    def get(cls, session_id: str, auth: str, repo=secret_share_repository) -> 'ShareSession':
        session = repo.get_session(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        i = cls.from_dict(session, repo=repo)
        if not i.get_user(auth):
            raise exceptions.ObjectDeniedException
        return i

    def get_user(self, user_id: str):
        return UUID(user_id) == self.master.uuid and self.master or self._users.get(user_id, None)

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid,
            master=self._master.to_dict(),
            last_update=self._last_update,
            alias=self._alias
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'ShareSession':
        from ssshare.domain.master import ShareSessionMaster
        i = cls(repo=repo)
        i._uuid = data['uuid']
        i._master = data.get('master') and ShareSessionMaster.from_dict(data['master'])
        i._last_update = data['last_update']
        i._alias = data['alias']
        return i

    @property
    def uuid(self) -> (None, UUID):
        return self._uuid

    def store(self) -> 'ShareSession':
        assert not self._uuid
        self._last_update = int(time.time())
        res = self._repo.store_session(self.to_dict())
        self._uuid = res['uuid']
        return self

    def update(self) -> 'ShareSession':
        assert self._uuid
        self._repo.update_session(self.to_dict())
        self._last_update = int(time.time())
        return self

    def delete(self) -> bool:
        assert self._uuid
        self._repo.delete_session(self.to_dict())
        return True

    def to_api(self, auth=None):
        users = [self.master.to_api(auth=auth)] + \
                [user.to_api(auth=auth) for user in list(self._users.values())]
        res = {
            'ttl': self.ttl,
            'users': users,
            'secret_sha256': self._secret and self._secret.sha256,
            'alias': self._alias
        }
        if auth and self.master and auth == str(self.master.uuid):
            res['secret'] = self._secret and self._secret.value
        return res