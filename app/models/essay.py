import datetime

from app import db
from enum import Enum

class EssayGrade(Enum):
    POOR = 'poor'
    FAIR = 'fair'
    SATISFACTORY = 'satisfactory'
    GOOD = 'good'
    VERY_GOOD = 'very good'
    EXCELLENT = 'excellent'

    @classmethod
    def has_key(cls, name):
        return name.upper() in cls.__members__


class EssaySuggestion(db.Model):
    __tablename__ = 'essay_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.Text, nullable=False)
    problem = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'), nullable=False)

    def __init__(self, area: str, problem: str, solution: str, essay_id: int):
        self.area = area
        self.problem = problem
        self.solution = solution
        self.essay_id = essay_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            'area': self.area,
            'problem': self.problem,
            'solution': self.solution
        }


class Essay(db.Model):
    """
    Model that represents a graded essay
    """
    __tablename__ = "essays"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Text, nullable=False)
    essay = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Enum(EssayGrade), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    suggestions = db.relationship(EssaySuggestion, backref='essay', lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Essay (id='{self.id}', topic='{self.topic}', user_id='{self.user_id}')>"

    def __init__(self, topic: str, essay: str, comment: str, grade: EssayGrade, user_id: int):
        self.topic = topic
        self.essay = essay
        self.comment = comment
        self.grade = grade
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
            'userId': self.user_id,
            'comment': self.comment,
            'grade': self.grade.name,
            'suggestions': [suggestion.serialized for suggestion in self.suggestions],
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
