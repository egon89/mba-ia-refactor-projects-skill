from datetime import timedelta

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from config import constants
from services import task_service, user_service
from utils.clock import utcnow
from utils.metrics import calculate_percentage


def _count_by_priority():
    rows = dict(
        db.session.query(Task.priority, db.func.count(Task.id)).group_by(Task.priority).all()
    )
    return {label: rows.get(priority, 0) for priority, label in constants.PRIORITY_LABELS.items()}


def _user_productivity():
    done_case = db.case((Task.status == constants.TASK_STATUS_DONE, 1), else_=0)
    rows = (
        db.session.query(Task.user_id, db.func.count(Task.id), db.func.sum(done_case))
        .group_by(Task.user_id)
        .all()
    )
    totals = {user_id: (total, completed) for user_id, total, completed in rows}

    productivity = []
    for user in User.query.all():
        total, completed = totals.get(user.id, (0, 0))
        productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })
    return productivity


def build_summary():
    now = utcnow()
    overdue_tasks = Task.query.filter(Task.overdue_filter(now)).all()
    recent_since = now - timedelta(days=constants.RECENT_ACTIVITY_DAYS)

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.query.count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': task_service.count_by_status(),
        'tasks_by_priority': _count_by_priority(),
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.query.filter(Task.created_at >= recent_since).count(),
            'tasks_completed_last_7_days': Task.query.filter(
                Task.status == constants.TASK_STATUS_DONE,
                Task.updated_at >= recent_since
            ).count(),
        },
        'user_productivity': _user_productivity(),
    }


def build_user_report(user_id):
    user = user_service.get_user(user_id)
    tasks = task_service.list_user_tasks(user_id)
    now = utcnow()

    by_status = {status: 0 for status in constants.TASK_STATUSES}
    for task in tasks:
        if task.status in by_status:
            by_status[task.status] += 1

    done = by_status[constants.TASK_STATUS_DONE]
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': len(tasks),
            'done': done,
            'pending': by_status[constants.TASK_STATUS_PENDING],
            'in_progress': by_status[constants.TASK_STATUS_IN_PROGRESS],
            'cancelled': by_status[constants.TASK_STATUS_CANCELLED],
            'overdue': sum(1 for task in tasks if task.is_overdue(now)),
            'high_priority': sum(
                1 for task in tasks if task.priority <= constants.HIGH_PRIORITY_THRESHOLD
            ),
            'completion_rate': calculate_percentage(done, len(tasks)),
        }
    }
