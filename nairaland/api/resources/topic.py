from flask import request
from flask_restful import Resource

from nairaland.api.resources.schemas import DataSchema, ErrorSchema, TopicSchema, UserSchema
from nairaland.extensions import mongo
from datetime import datetime


class DataInfo(Resource):
    """Get information about the current state of the nairaland data dump.
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
        data = {'as_at': datetime.today()}
        schema = DataSchema()
        query = list(mongo.db.topics.find())
        data['topic_count'] = len(query)
        comments_pipeline = [
            {"$unwind": "$comments"},
            {"$group":{"_id" : None, "$count": "comments"}}]
        data['comment_count'] = list(mongo.db.topics.aggregate(comments_pipeline))[0].get('comments')
        users_pipeline = [
            {
                "$unwind": "$comments"
            },
            {
                "$unwind": "$comments.user"
            },
            {"$group":
                 {"_id": '$comments.user'}}

        ]
        data['user_count'] = len(list(mongo.db.topics.aggregate(users_pipeline)))
        return {"info": schema.dump(data).data}


class UserResource(Resource):
    """Get users.
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
        data = {'as_at': datetime.today()}
        schema = UserSchema()
        pipeline = [
            {
                "$unwind": "$comments"
            },
            {
                "$unwind": "$comments.user"
            },
            {"$group":
                 {"_id": '$comments.user',
                  "count": {"$sum": 1}}}

        ]
        data['users'] = list(mongo.db.topics.aggregate(pipeline))

        import pprint
        pprint.pprint(data)
        return {"info": schema.dump(data).data}


class TopicResource(Resource):
    """Get a single topic using it's id.

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
        return {"data": schema.dump(topic).data}


class TopicList(Resource):
    """Get a list of random topics. If limit is not specified, it defaults to 10 random topics.
    ---
    get:
      tags:
        - api
      parameters:
        - in: query
          name: limit
          schema:
            type: integer
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
        limit = request.args.get('limit', 10)
        schema = TopicSchema(many=True)
        topics = mongo.db.topics.aggregate([{"$sample": {"size": int(limit)}}])
        return {"data": schema.dump(topics).data}


class UserCommentSearchResource(Resource):
    """Search for a comment from a user. You can choose to return either topics the user's comment appeared in or just the information about the comment.

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
            description: Comment does not exist    
    """

    def get(self):
        topic_id, page_id, username, to_return = request.args.get('topicId', None), request.args.get('pageId', None), request.args.get('username', None), request.args.get('r', 'all')
        query = {}
        if topic_id:
            query['topic_id'] = topic_id
        elif page_id:
            query['comments.pageId'] = int(page_id)
        query['comments.user'] = username
        schema = TopicSchema(many=True)
        pipeline = [
            {"$match": query},
            {"$unwind": "$comments"},
            {"$match": query}
        ]
        comments = mongo.db.topics.aggregate(pipeline)
        return {"data": schema.dump(comments).data}


class TextSearchResource(Resource):
    """Search for text in the dump. This is done on both the db and memory layer so it might take some time to return results.

      ---
      get:
        tags:
          - api
        parameters:
          - in: query
            name: text
            required: true
            schema:
              type: string
            description: Text to search
          - in: query
            name: topic
            required: true
            schema:
              type: boolean
            description: Is the text a topic?
          - in: query
            name: r
            required: false
            schema:
              type: string
            description: Return topics or comments
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
        text, page_id, username, topic, limit = request.args.get('text', None), \
                                                request.args.get('pageId', None), \
                                                request.args.get('username', None), \
                                                request.args.get('topic', 0), \
                                                request.args.get('limit', 3)

        if not text:
            return {"error": ErrorSchema().dump({"error_code": "E-003", "message": "Missing field ['text']"}).data}
        if topic:
            texts = mongo.db.topics.find({"topic": {"$regex": text}})
        else:
            pipeline = [
                {"$match": {"comments.text": {"$regex": text}}},
                {"$unwind": "$comments"},
                {"$match": {"comments.text": {"$regex": text}}},
                {"$limit": int(limit)}
            ]
            if username:
                pipeline[0]['$match']['comments.user'] = username
                pipeline[2]['$match']['comments.user'] = username
            if page_id:
                pipeline[0]['$match']['comments.pageId'] = int(page_id)
                pipeline[2]['$match']['comments.pageId'] = int(page_id)
            texts = mongo.db.topics.aggregate(pipeline)
        schema = TopicSchema(many=True)
        return {"data": schema.dump(texts).data}
