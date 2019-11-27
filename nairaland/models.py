from nairaland.extensions import db

class Comment(db.EmbeddedDocument):
    text = db.StringField()
    user  = db.StringField()
    timestamp = db.StringField()
    attachments = db.ListField(db.StringField())
    sex = db.StringField()
    pageId = db.IntField()

    def __repr__(self):
        return '<Comment(user={self.user!r})>'.format(self=self)

class Topic(db.DynamicDocument):
    meta = {
        'collection': 'Topic'
    }
    class_ = db.StringField()
    topic_id = db.StringField()
    topic = db.StringField()
    url = db.StringField()
    topic_id = db.StringField()
    view_count = db.IntField()
    comments = db.ListField(db.EmbeddedDocumentField(Comment))

    def __repr__(self):
        return '<Topic(name={self.topic!r})>'.format(self=self)

