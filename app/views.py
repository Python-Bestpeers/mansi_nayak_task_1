from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from .forms import LoginForm, SignUpForm, TaskForm, CommentForm
from .models import Task, User, Comment
from django.core.mail import send_mail
from django.conf import settings


class Home(TemplateView):
    template_name = "home.html"

    def get(self, request):
        return render(request, self.template_name)


class SignUpView(TemplateView):
    template_name = "signin/register.html"

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # Process the form submission
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully! Please log in."
            )
            return redirect("login")

        return render(request, self.template_name, {"form": form})


class LoginView(TemplateView):
    template_name = "signin/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("listsoftask")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


class CreateTaskView(TemplateView):
    template_name = "create_task.html"

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        form = TaskForm()
        context = {
            "form": form,
            "users": users,
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()

            # Send Mail
            assigned_to = task.assigned_to
            subject = f"New Task Assigned: {task.title}"
            message = f"You have been assigned a new task: {task.title}\nDetail: {task.detail}\nPriority: {task.get_priority_display()}\nDue_Date: {task.due_date}"
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [assigned_to.email],
                fail_silently=False,
            )
            return redirect("listsoftask")
        else:
            return render(request, self.template_name, {"form": form})


class UpdateTaskView(TemplateView):
    template_name = "task_update.html"

    def get(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(instance=task)
        context = {
            "form": form,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()

        form = TaskForm(request.POST, instance=task)
        context = {
            "form": form,
            "task": task,
        }
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect("listsoftask")
        return render(request, self.template_name, context=context)


class DeleteTaskView(TemplateView):
    def post(self, request, pk):
        task = Task.objects.filter(id=pk).first()
        task.delete()
        return redirect("listsoftask")


class DetailTaskView(TemplateView):
    template_name = "task_detail.html"

    def get(self, request, pk):
        task = Task.objects.get(id=pk)
        comments = Comment.objects.filter(task=task)
        form = CommentForm()
        context = {
            "task": task,
            "comments": comments,
            "form": form,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, pk):
        task = Task.objects.get(id=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.save(commit=False)
            text.user = request.user
            text.task = task
            text.save()
            return redirect("listsoftask")
        comments = Comment.objects.filter(task=task)
        context = {
            "task": task,
            "comments": comments,
            "form": form,
        }
        return render(request, self.template_name, context)


class TaskListView(TemplateView):
    template_name = "task_list.html"

    def get(self, request):
        users = User.objects.all()
        task = Task.objects.all()

        assigned_to = request.GET.get("assigned_to")
        status = request.GET.get("status")
        due_date = request.GET.get("due_date")

        if assigned_to:
            task = task.filter(assigned_to_id=assigned_to)
        if status:
            task = task.filter(status=status)
        if due_date:
            task = task.filter(due_date=due_date)

        context = {
            "users": users,
            "task": task,
            "assigned_to": assigned_to,
            "status": status,
            "due_date": due_date,
        }
        return render(request, self.template_name, context=context)


class UserListView(TemplateView):
    template_name = "user_list.html"

    def get(self, request):
        user = User.objects.all()
        context = {"user": user}
        return render(request, self.template_name, context=context)
