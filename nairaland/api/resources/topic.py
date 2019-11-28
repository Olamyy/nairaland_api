from flask import request
from flask_restful import Resource

from nairaland.api.resources.schemas import DataSchema, CommentSchema, ErrorSchema, TopicSchema
from nairaland.extensions import mongo
from datetime import datetime

from nairaland.utils import flatten


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
        comments = flatten([entry.get('comments') for entry in query])
        data['comment_count'] = len(comments)
        data['user_count'] = len(list(set([entry.get('user') for entry in comments])))
        print(schema.dump(data).data)
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
        return {"topic": schema.dump(topic).data}


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
        return {"topics": schema.dump(topics).data}


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
            description: Comment does not exist    
    """

    def get(self):
        topic_id, page_id, username, to_return = request.args.get('topicId', None), request.args.get('pageId', None), request.args.get('username', None), request.args.get('r', 'topics')
        query = {}
        if topic_id:
            query['topic_id'] = topic_id
        elif page_id:
            query['comments.pageId'] = int(page_id)
        query['comments.user'] = username
        topics = mongo.db.topics.find(query)
        if to_return == "topics":
            schema = TopicSchema(many=True)
            return {"topics": schema.dump(topics).data}
        else:
            schema = CommentSchema(many=True)
            topics = list(topics)
            if not topics:
                return {"topics": ErrorSchema().dump({"error_code": "E-002", "message": "Resource Does Not Exist"}).data}
            comments = flatten([entry.get('comments') for entry in topics])
            if page_id:
                user_comments = [entry for entry in comments if (entry.get('user') == username and entry.get('pageId') == int(page_id))]
            else:
                user_comments = [entry for entry in comments if entry.get('user') == username]
            return {"topics": schema.dump(user_comments).data}


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
        text, to_return, page_id, username, topic = request.args.get('text', None), \
                                                    request.args.get('r', 'topics'), \
                                                    request.args.get('pageId', None), \
                                                    request.args.get('username', None), \
                                                    request.args.get('topic', 0)
        if not text:
            return {"error": ErrorSchema().dump({"error_code": "E-003", "message": "Missing field ['text']"}).data}
        if topic:
            texts = mongo.db.topics.find({"topic": {"$regex": text}})
        else:
            return {'response': {"message": "Comment Search is not functional. Check back later."}}
            texts = mongo.db.topics.find({"$text": {"$search": text}}, ({'score': {"$meta": 'textScore'}}))
        if to_return == "topics":
            schema = TopicSchema(many=True)
            return {"topics": schema.dump(texts).data}
        else:
            schema = CommentSchema(many=True)
            texts = list(texts)
            comments = flatten([entry.get('comments') for entry in texts])
            if username:
                if page_id:
                    user_comments = [entry for entry in comments if (entry.get('user') == username and entry.get('pageId') == int(page_id))]
                else:
                    user_comments = [entry for entry in comments if entry.get('user') == username]
                return {"topics": schema.dump(user_comments).data}
            else:
                return {"topics": schema.dump(comments).data}
