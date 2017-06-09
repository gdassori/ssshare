import flask
from flask.views import MethodView
from ssshare import exceptions
from ssshare.blueprints import validators
from ssshare.domain.master import SharedSessionMaster
from ssshare.domain.split_session import SplitSession

bp = flask.Blueprint('split', __name__)


class SplitSessionCreateView(MethodView):
    @validators.validate(validators.SplitSessionCreateValidator)
    def post(self, params=None):
        user = SharedSessionMaster.new(alias=params['user_alias'])
        session = SplitSession.new(master=user, alias=params['session_alias']).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": str(session.uuid)
            }
        )


class SplitSessionSharedView(MethodView):
    @validators.validate(validators.SplitSessionGetValidator)
    def get(self, session_id, params=None):
        session = SplitSession.get(session_id, auth=params['auth'])
        if not session:
            raise exceptions.DomainObjectNotFoundException
        if not session.ttl:
            raise exceptions.DomainObjectExpiredException
        return flask.jsonify(
            {
                "session": session.to_api(auth=params['auth']),
                "session_id": str(session.uuid)
            }
        )

    @validators.validate(validators.SplitSessionEditValidator)
    def put(self, session_id, params=None):
        session = SplitSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        user = params.get('auth') and session.get_user(params['auth'], alias=str(params['user_alias'])) \
               or session.join(params['user_alias'])
        if not user:
            raise exceptions.ObjectDeniedException
        if user.is_master:
            session.set_secret_from_payload(dict(params))
        session.update()
        return flask.jsonify(
            {
                "session": session.to_api(auth=str(user.uuid)),
                "session_id": str(session.uuid)
            }
        )

bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'POST'],
    view_func=SplitSessionSharedView.as_view('split_session_shared')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SplitSessionCreateView.as_view('split_session_create'))