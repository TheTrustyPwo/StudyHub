import datetime
import uuid

from app import db


class ConversationMember(db.Model):
    """
    Model that represents a conversation member
    """
    __tablename__ = "conversation_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ConversationMember (id='{self.id}', user='{self.user_id}', conversation='{self.conversation_id}')>"

    def __init__(self, user_id: int, conversation_id: str, is_admin: bool = False):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.is_admin = is_admin

    def save(self):
        """
        Persist the Conversation Member in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(conversation_member_id):
        """
        Filter a Conversation Member by id
        :param conversation_member_id
        :return: Conversation Member or None
        """
        return ConversationMember.query.filter_by(id=conversation_member_id).first()
