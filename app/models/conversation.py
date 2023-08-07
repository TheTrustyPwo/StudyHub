import datetime
import uuid

from app import db


class Conversation(db.Model):
    """
    Model that represents a conversation
    """
    __tablename__ = "conversations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(36), nullable=True)
    description = db.Column(db.String(1024), nullable=True)
    date_created = db.Column(db.DateTime, index=True, nullable=False, default=datetime.datetime.utcnow)
    is_group = db.Column(db.Boolean, nullable=False)

    users = db.relationship('User', secondary='conversation_members', back_populates='conversations', lazy='dynamic')
    messages = db.relationship('Message', foreign_keys='Message.conversation_id', back_populates='conversation', lazy='dynamic')

    def __repr__(self):
        return f"<conversation (id='{self.id}', name='{self.name}', description='{self.description}', is_group='{self.is_group}')>"

    def __init__(self, name: str = None, description: str = None, *, is_group: bool):
        if is_group:
            assert name is not None
            description = description or "Group Description"

        self.name = name
        self.description = description
        self.is_group = is_group

    def save(self):
        """
        Persist the Conversation in the database
        """
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "isGroup": self.is_group,
            "dateCreated": self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            "userIds": [user.id for user in self.users]
        }

    @staticmethod
    def get_by_id(Conversation_id):
        """
        Filter a Conversation by id
        :param Conversation_id
        :return: Conversation or None
        """
        return Conversation.query.filter_by(id=Conversation_id).first()
