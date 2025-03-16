import random
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from faker import Faker
from django.contrib.auth import get_user_model
from tasks.models import Task
from users.models import User
fake = Faker()

def create_task_batch(users, batch_size):
    tasks = [
        Task(
            title=fake.sentence(),
            description=fake.paragraph(),
            priority=random.choice([Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH]),
            due_date=now() + timedelta(days=random.randint(1, 365)),
            status=random.choice([Task.Status.PENDING, Task.Status.IN_PROGRESS, Task.Status.COMPLETED]),
            assigned_to=random.choice(users),
            created_by=random.choice(users),
        )
        for _ in range(batch_size)
    ]
    Task.objects.bulk_create(tasks)

class Command(BaseCommand):
    help = "Generate random tasks"


    def handle(self, *args, **options):
        total_records = 100000
        num_threads = 4
        
        users = list(User.objects.all())
        if not users:
            print("No users found. Please create users first.")
            return

        batch_size = total_records // num_threads 
        print(f"Generating {total_records} tasks using {num_threads} threads...")

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_task_batch, users, batch_size) for _ in range(num_threads)]

        print(f"{total_records} tasks created successfully")
