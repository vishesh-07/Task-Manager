from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.EmailField(source='created_by.email', read_only=True)
    assigned_to = serializers.EmailField(source='assigned_to.email', read_only=True)
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "created_by", "assigned_to"]
