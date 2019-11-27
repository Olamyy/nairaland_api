from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from nairaland.extensions import mongo
from marshmallow import Schema, fields, pprint
from datetime import datetime
import pymongo


def flatten(data):
  return [y for x in data for y in x]

class CommentSchema(Schema):
    text = fields.String()
    user  = fields.String()
    timestamp = fields.String()
    attachments = fields.List(fields.String())
    sex = fields.String()
    pageId = fields.Int()

    def __repr__(self):
        return '<Comment(user={self.user!r})>'.format(self=self)

class TopicSchema(Schema):
    class_ = fields.String()
    topic_id = fields.String()
    topic = fields.String()
    url = fields.String()
    topic_id = fields.String()
    view_count = fields.Int()
    comments = fields.List(fields.Nested(CommentSchema()))

    def __repr__(self):
        return '<Topic(name={self.topic!r})>'.format(self=self)

class DataSchema(Schema):
    topic_count = fields.Int()
    comment_count = fields.Int()
    user_count = fields.Int()
    as_at = fields.Date()

    def __repr__(self):
        return '<Info(name={self.count!r})>'.format(self=self)

class DataInfo(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  topic: TopicSchema
        404:
          description: Topic does not exist    
    """
    def get(self):
        data = {'as_at':datetime.today()}
        schema = DataSchema()
        query = list(mongo.db.topics.find())
        data['topics'] = len(query)
        comments = flatten([entry.get('comments') for entry in query])
        data['comment_count'] = len(comments)
        data['user_count'] = len(list(set([entry.get('user') for entry in comments])))
        print(schema.dump(data).data)
        return {"info": schema.dump(data).data}          

class TopicResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: topic_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  topic: TopicSchema
        404:
          description: Topic does not exist    
    """

    def get(self, topic_id):
        schema = TopicSchema()
        topic = mongo.db.topics.find_one({"topic_id": str(topic_id)})
        return {"topic": schema.dump(topic).data}

class TopicList(Resource):
    """get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/TopicSchema'
    """

    def get(self):
        schema = TopicSchema(many=True)
        topics = mongo.db.topics.find()
        return {"topics": schema.dump(topics).data}


class UserCommentSearchResource(Resource):
    """Search for a comment from a user.

      ---
      get:
        tags:
          - api
        parameters:
          - in: query
            name: username
            required: true
            schema:
              type: string
            description: Search for a comment from a user.
          - in: query
            name: page_id
            required: false
            schema:
              type: integer
            description: Search for a text on this pageId.
          - in: query
            name: topic_id
            required: false
            schema:
              type: integer
            description: Search for a text on this topicId.
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    topic: TopicSchema
          404:
            description: Topic does not exist    
    """
    def get(self):
        print(request.args)
        topic_id, page_id, username = request.args.get('topic_id', None), request.args.get('page_id', None), request.args.get('username', None)
        schema = TopicSchema(many=True)
        query = {}
        if topic_id:
            query['topic_id'] = topic_id
        elif page_id:
            query['comments.pageId'] = page_id
        query['comments.user'] = username
        print(query)
        topics = mongo.db.topics.find({'comments.user': "solo2"})
        return {"topics": schema.dump(topics).data}