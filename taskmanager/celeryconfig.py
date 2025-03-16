from celery.schedules import crontab
from .celery import app  # Import the Celery instance

app.conf.beat_schedule = {
    "task_deadline_reminder_every_hour": {
        "task": "tasks.tasks.send_task_deadline_reminder",
        "schedule": crontab(minute=0, hour="*"),
    },
}
