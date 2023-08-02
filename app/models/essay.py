import datetime

from app import db
from enum import Enum

class EssayEvaluation(Enum):
    POOR = 'poor'
    FAIR = 'fair'
    SATISFACTORY = 'satisfactory'
    GOOD = 'good'
    VERY_GOOD = 'very_good'
    EXCELLENT = 'excellent'

    @classmethod
    def has_key(cls, name):
        return name.upper() in cls.__members__


class EssayCompliment(db.Model):
    __tablename__ = 'essay_compliments'

    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.Text, nullable=False)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'), nullable=False)

    def __init__(self, remarks: str, essay_id: int):
        self.remarks = remarks
        self.essay_id = essay_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            'remarks': self.remarks
        }


class EssayCriticism(db.Model):
    __tablename__ = 'essay_criticism'

    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.Text, nullable=False)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'), nullable=False)

    def __init__(self, remarks: str, essay_id: int):
        self.remarks = remarks
        self.essay_id = essay_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            'remarks': self.remarks
        }



class Essay(db.Model):
    """
    Model that represents a graded essay
    """
    __tablename__ = "essays"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Text, nullable=False)
    essay = db.Column(db.Text, nullable=False)
    evaluation = db.Column(db.Enum(EssayEvaluation), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    compliments = db.relationship(EssayCompliment, backref='essay', lazy="dynamic", cascade="all, delete-orphan")
    criticisms = db.relationship(EssayCriticism, backref='essay', lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Essay (id='{self.id}', topic='{self.topic}', user_id='{self.user_id}')>"

    def __init__(self, topic: str, essay: str, evaluation: EssayEvaluation, user_id: int):
        self.topic = topic
        self.essay = essay
        self.evaluation = evaluation
        self.user_id = user_id

    def save(self):
        """
        Persist the essay in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'essay': self.essay,
            'user_id': self.user_id,
            'evaluation': self.evaluation.name,
            'compliments': [o.serialized for o in self.compliments],
            'criticisms': [o.serialized for o in self.criticisms],
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def get_by_id(essay_id):
        """
        Filter an essay by id
        :param essay_id
        :return: Reply or None
        """
        return Essay.query.filter_by(id=essay_id).first()
