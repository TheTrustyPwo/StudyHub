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

    def __repr__(self):
        return f"<Message (id='{self.id}', sender='{self.sender_id}', conversation='{self.conversation_id}', content='{self.content})>"

    def __init__(self, sender_id: int, conversation_id: str, content: str):
        self.sender_id = sender_id
        self.conversation_id = conversation_id
        self.content = content

    def save(self):
        """
        Persist the message in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(message_id):
        """
        Filter a message by id
        :param message_id
        :return: Message or None
        """
        return Message.query.filter_by(id=message_id).first()
