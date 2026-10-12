from database import db
from config.constants import CLOSED_TASK_STATUSES, DEFAULT_PRIORITY, TASK_STATUS_PENDING
from utils.clock import utcnow

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=TASK_STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['title'] = self.title
        data['description'] = self.description
        data['status'] = self.status
        data['priority'] = self.priority
        data['user_id'] = self.user_id
        data['category_id'] = self.category_id
        data['created_at'] = str(self.created_at)
        data['updated_at'] = str(self.updated_at)
        data['due_date'] = str(self.due_date) if self.due_date else None
        data['tags'] = self.tags.split(',') if self.tags else []
        return data

    def is_overdue(self, now=None):
        if not self.due_date:
            return False
        return self.due_date < (now or utcnow()) and self.status not in CLOSED_TASK_STATUSES

    @classmethod
    def overdue_filter(cls, now):
        """Mesma regra de is_overdue(), como condição SQL."""
        return db.and_(
            cls.due_date.isnot(None),
            cls.due_date < now,
            cls.status.notin_(CLOSED_TASK_STATUSES),
        )
