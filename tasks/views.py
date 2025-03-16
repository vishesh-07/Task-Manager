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

from users.models import User
from .serializers import TaskSerializer
from .models import Task

# Route - /tasks/


class TasksViewSet(GenericViewSet, ListModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        try:
            task = get_object_or_404(Task, id=kwargs.get("pk"))
            serializer = self.serializer_class(task)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
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
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(tasks, many=True)
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

            serializer = self.get_serializer(task)
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
