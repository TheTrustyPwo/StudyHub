import datetime

from app import db


class Message(db.Model):
    """
    Model that represents a message
    """
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, nullable=False, default=datetime.datetime.utcnow)

    sender = db.relationship('User', back_populates='messages')
    conversation = db.relationship('Conversation', back_populates='messages')
    read_users = db.relationship('ReadMessage', back_populates='message')

    def __repr__(self):
        return f"<Message (id='{self.id}')>"

    def __init__(self, sender_id: int, conversation_id: str, content: str):
        self.sender_id = sender_id
        self.conversation_id = conversation_id
        self.content = content

    def save(self):
        """
        Persist the message in the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the message from the database
        """
        db.session.delete(self)
        db.session.commit()

    @property
    def read_by_all(self) -> bool:
        """
        Check if the message has been read by all users in the conversation.

        :return: True if the message has been read by all users, False otherwise.
        :rtype: bool
        """
        conversation_users = set(user.id for user in self.conversation.users)
        read_users = set(read_user.user_id for read_user in self.read_users)

        return conversation_users == read_users

    @property
    def serialized(self):
        return {
            'id': self.id,
            'senderId': self.sender_id,
            'conversationId': self.conversation_id,
            'content': self.content,
            'readUserIds': [data.user.id for data in self.read_users],
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    @property
    def serialized_min(self):
        return {
            'id': self.id,
            'senderId': self.sender_id,
            'content': self.content,
            'readUserIds': [data.user.id for data in self.read_users],
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def get_by_id(message_id):
        """
        Filter a message by id
        :param message_id
        :return: Message or None
        """
        return Message.query.filter_by(id=message_id).first()


class ReadMessage(db.Model):
    """
    Model that represents a read message
    """
    __tablename__ = "read_messages"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    message = db.relationship('Message', back_populates='read_users')
    user = db.relationship('User', back_populates='read_messages')

    def __repr__(self):
        return f"<ReadMessage (id='{self.id}')>"

    def __init__(self, message_id: int, user_id: int):
        self.message_id = message_id
        self.user_id = user_id

    def save(self):
        """
        Persist the read message data in the database
        """
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @staticmethod
    def get_by_id(read_message_id):
        """
        Filter a read message by id
        :param read_message_id
        :return: Message or None
        """
        return ReadMessage.query.filter_by(id=read_message_id).first()
