from django.conf import settings
from django.core.mail import send_mail


def send_task_assigned_email(assigned_to, task):
    subject = f"New Task Assigned: {task.title}"
    message = f"You have been assigned a new task: {task.title}\nDetail: {task.detail}\nPriority: {task.get_priority_display()}\nDue Date: {task.due_date}"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [assigned_to.email],
        fail_silently=False,
    )


def send_task_update_email(task):
    subject = "Task Updated"
    message = (
        f"Dear {task.assigned_to.username},\n\n"
        f"The task '{task.title}' has been updated by the creator.\n\n"
        f"So Please check the Task."
    )
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [task.assigned_to.email],
        fail_silently=False,
    )
