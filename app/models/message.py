import datetime

from app import db


class Message(db.Model):
    """
    Model that represents a message
    """
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Message (id='{self.id}', sender_id='{self.sender_id}', recipient_id='{self.recipient_id}', content='{self.content}, timestamp='{self.timestamp}')>"

    def __init__(self, sender_id: int, recipient_id: int, content: str):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
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
