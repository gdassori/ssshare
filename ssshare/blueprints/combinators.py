import uuid
import functools
import flask
from flask import json
from pycomb import combinators
from pycomb.exceptions import PyCombValidationError
from ssshare import exceptions, settings


def is_uuid(value):
    try:
        assert value
        return uuid.UUID(value)
    except (TypeError, ValueError, AssertionError):
        return


def validate(validation_class, silent=not settings.DEBUG):
    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*a, **kw):
            if flask.request.method == 'GET':
                p = {k: v for k, v in flask.request.values and flask.request.values.items() or {}}
            else:
                try:
                    p = flask.request.data and json.loads(flask.request.data.decode())
                except Exception:
                    raise exceptions.WrongParametersException
            if silent:
                try:
                    validation_class(p)
                except PyCombValidationError:
                    raise exceptions.WrongParametersException
            else:
                validation_class(p)
            return fun(*a, params=p, **kw)
        return wrapper
    return decorator


UUIDCombinator = combinators.subtype(
    combinators.String,
    is_uuid
)

ShareSessionDataCombinator = combinators.struct(
    {
        "secret": combinators.struct(
            {
                "secret": combinators.String,
                "shares": combinators.Int,
                "quorum": combinators.Int
            }
        )
    }
)

ShareSessionCombinator = combinators.subtype(
    ShareSessionDataCombinator,
    lambda x: x['secret']['shares'] >= x['secret']['quorum']
)



ShareSessionCreateCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
        "session_alias": combinators.String
    },
    strict=True
)

ShareSessionGetCombinator = combinators.struct(
    {
        "auth": UUIDCombinator
    },
    strict=True
)


ShareSessionJoinCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
    },
    strict=True
)

ShareSessionMasterEditCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
        "auth": combinators.String,
        "session": ShareSessionCombinator
    },
    strict=True
)

ShareSessionEditCombinator = combinators.union(
    ShareSessionJoinCombinator,
    ShareSessionMasterEditCombinator
)