from marshmallow import Schema, fields


class ErrorSchema(Schema):
    error_code = fields.String()
    message = fields.String()


class CommentSchema(Schema):
    text = fields.String()
    user = fields.String()
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


class UserSchema(Schema):
    users = fields.List(fields.Dict())
    as_at = fields.Date()

