from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")

    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    priority = models.CharField(
        _("Priority"), max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    due_date = models.DateTimeField(_("Due Date"), null=True, blank=True)
    status = models.CharField(
        _("Status"), max_length=15, choices=Status.choices, default=Status.PENDING
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("Assigned To"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.title
