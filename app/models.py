from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel

# Create your models here.

# User


class User(AbstractUser, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# Task


class Task(TimeStampedModel):
    STATUS = [
        ("Complete", "Complete"),
        ("Inprogress", "Inprogress"),
    ]
    PRIORITY = [
        ("Major", "Major"),
        ("Intermediate", "Intermediate"),
        ("Minor", "Minor"),
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    detail = models.TextField()
    due_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=200, choices=STATUS, default="Inprogress"
    )
    priority = models.CharField(
        max_length=200, choices=PRIORITY, default="Intermediate"
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tasks_assigned_by"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tasks_assigned_to"
    )

    def __str__(self):
        return self.title


# Comment


class Comment(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comment"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return self.text
