import os
from pathlib import Path
from celery import shared_task
from django.core.mail import send_mail
from datetime import timedelta
from django.utils.timezone import now
from .models import Task

@shared_task(bind=True, default_retry_delay=60, max_retries=5)
def send_task_assignment_email(self,task_id):
    try:
        task = Task.objects.get(id=task_id)
        send_mail(
            subject="Task Assigned",
            message=f"You have been assigned a new task: {task.title}",
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=[task.assigned_to.email]
        )
    except Exception as e:
        raise self.retry(exc=e)

@shared_task
def send_task_deadline_reminder(self):
    try:
        tasks = Task.objects.filter(due_date__lte=now() + timedelta(hours=24), status=Task.Status.PENDING)
        for task in tasks:
            send_mail(
                subject="Task Deadline Approaching",
                message=f"Your task '{task.title}' is due soon.",
                from_email=os.getenv("EMAIL_HOST_USER"),
                recipient_list=[task.assigned_to.email]
            )
    except Exception as e:
        raise self.retry(exc=e)