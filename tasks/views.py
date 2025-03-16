from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from urllib.parse import urlencode
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
from django.http import HttpResponse
from io import StringIO
import csv
from rest_framework.throttling import UserRateThrottle

from users.models import User
from .serializers import TaskSerializer
from .models import Task
from .tasks import send_task_assignment_email

# Route - /tasks/


class TasksViewSet(GenericViewSet, ListModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    throttle_classes = [UserRateThrottle]

    def retrieve(self, request, *args, **kwargs):
        try:
            task = get_object_or_404(Task, id=kwargs.get("pk"))
            serializer = self.serializer_class(task)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    def get_cache_key(self, request):
        params = request.GET.dict()
        sorted_params = sorted(params.items())
        encoded = urlencode(sorted_params)
        return f"tasks_list:{request.user.id}:{encoded}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data, status=HTTP_200_OK)
        try:
            title = request.GET.get("title", None)
            description = request.GET.get("description", None)
            priority = request.GET.get("priority", None)
            due_date = request.GET.get("due_date", None)
            status = request.GET.get("status", None)
            assigned_to = request.GET.get("assigned_to", None)

            filters = {}
            if title:
                filters["title__icontains"] = title
            if description:
                filters["description__icontains"] = description
            if priority:
                filters["priority__iexact"] = priority
            if due_date:
                filters["due_date__date"] = due_date
            if status:
                filters["status__iexact"] = status
            if assigned_to:
                filters["assigned_to__email__iexact"] = assigned_to

            tasks = self.queryset.filter(**filters)
            page = self.paginate_queryset(tasks)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set(cache_key, serializer.data, timeout=60)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(tasks, many=True)
            cache.set(cache_key, serializer.data, 60)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            title = request.data.get("title")
            description = request.data.get("description")
            priority = request.data.get("priority")
            due_date = request.data.get("due_date")
            status = request.data.get("status")
            assigned_to = request.data.get("assigned_to")

            if not title or not assigned_to:
                return Response(
                    {"message": "Title and Assigned To fields are required"},
                    status=HTTP_400_BAD_REQUEST,
                )

            assigned_to = get_object_or_404(User, email=assigned_to)

            task = Task.objects.create(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                status=status,
                assigned_to=assigned_to,
                created_by=request.user,
            )
            send_task_assignment_email.delay(task.id)

            serializer = self.get_serializer(task)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "tasks",
                {
                    "type": "send_task_update",
                    "message": serializer.data
                }
            )
            return Response(
                {"message": "Task Created", "data": serializer.data},
                status=HTTP_201_CREATED,
            )
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            task = get_object_or_404(Task, id=kwargs.get("pk"), created_by=request.user)
            serializer = self.serializer_class(task, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'task_{kwargs.get("pk")}',  # Specific task group
                {
                    "type": "send_task_update",
                    "message": serializer.data
                }
            )
            return Response(
                {"message": "Task Updated", "data": serializer.data}, status=HTTP_200_OK
            )
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            task = get_object_or_404(Task, id=kwargs.get("pk"), created_by=request.user)
            task.delete()
            return Response({"message": "Task Deleted"}, status=HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"], url_path="report")
    def generate_report(self, request):
        try:
            tasks = Task.objects.values("priority", "status")

            def count_completed():
                return tasks.filter(status=Task.Status.COMPLETED).count()

            def count_pending():
                return tasks.filter(status=Task.Status.PENDING).count()

            def categorize_by_priority():
                priority_counts = Counter(task["priority"] for task in tasks)
                return dict(priority_counts)

            with ThreadPoolExecutor(max_workers=3) as executor:
                completed_future = executor.submit(count_completed)
                pending_future = executor.submit(count_pending)
                priority_future = executor.submit(categorize_by_priority)

                completed_count = completed_future.result()
                pending_count = pending_future.result()
                priority_stats = priority_future.result()

            return Response(
                {
                    "completed_tasks": completed_count,
                    "pending_tasks": pending_count,
                    "tasks_by_priority": priority_stats,
                },
                status=HTTP_200_OK,
            )

        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["GET"], url_path="export")
    def export_tasks(self, request):
        try:
            def generate_csv():
                tasks = Task.objects.all().values("title", "description", "priority", "due_date", "status", "created_by__email", "assigned_to__email")
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=["title", "description", "priority", "due_date", "status", "created_by__email", "assigned_to__email"])
                writer.writeheader()
                for task in tasks:
                    writer.writerow(task)
                output.seek(0)
                return output.getvalue()

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generate_csv)
                csv_data = future.result()

            response = HttpResponse(csv_data, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=tasks_export.csv"
            return response

        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)