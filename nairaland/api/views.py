from flask import Blueprint, current_app
from flask_restful import Api

from nairaland.extensions import apispec
from nairaland.api.resources import TopicResource, TopicList, DataInfo, UserCommentSearchResource
from nairaland.api.resources.topic import TopicSchema, DataSchema


blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint)


api.add_resource(TopicResource, '/topic/<int:topic_id>')
api.add_resource(TopicList, '/topics')
api.add_resource(DataInfo, '/info')
api.add_resource(UserCommentSearchResource, '/user/search/')



@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("TopicSchema", schema=TopicSchema)
    apispec.spec.path(view=DataInfo, app=current_app)
    apispec.spec.path(view=UserCommentSearchResource, app=current_app)
    apispec.spec.path(view=TopicResource, app=current_app)
    apispec.spec.path(view=TopicList, app=current_app)
