from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from .email_utils import send_task_assigned_email, send_task_update_email
from .forms import CommentForm, LoginForm, SignUpForm, TaskForm, TaskStatusForm
from .models import Comment, Task, User


class Home(TemplateView):
    """
    View to render the home page.
    """

    template_name = "home.html"

    def get(self, request):
        """
        Handle GET requests for the home page.
        """
        return render(request, self.template_name)


class SignUpView(TemplateView):
    """
    View to handle user registration.
    """

    template_name = "signin/register.html"

    def get(self, request):
        """
        Render the registration form for a GET request.
        """
        form = SignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Process the registration form for a POST request.
        """
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully! Please log in."
            )
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class LoginView(TemplateView):
    """
    View to handle user login.
    """

    template_name = "signin/login.html"

    def get(self, request):
        """
        Render the login form. Redirects if the user is already authenticated.
        """
        if request.user.is_authenticated:
            return redirect("home")
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Authenticate the user and log them in if credentials are valid.
        """
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("task_list")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    """
    View to log out the user.
    """

    def get(self, request):
        """
        Log out the user and redirect to the home page.
        """
        logout(request)
        return redirect("home")


class CreateTaskView(TemplateView):
    """
    View to create a new task.
    """

    template_name = "create_task.html"

    def get(self, request):
        """
        Render the task creation form.
        """
        users = User.objects.exclude(id=request.user.id)
        form = TaskForm()
        context = {"form": form, "users": users}
        return render(request, self.template_name, context=context)

    def post(self, request):
        """
        Process the task creation form.
        """
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            send_task_assigned_email(task.assigned_to, task)
            return redirect("task_list")
        return render(request, self.template_name, {"form": form})


class UpdateTaskView(TemplateView):
    """
    View to update an existing task.
    """

    template_name = "task_update.html"

    def get(self, request, pk):
        """
        Render the task update form with existing task data.
        """
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(instance=task)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        """
        Process the task update form.
        """
        task = Task.objects.filter(id=pk).first()
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task_update = form.save()
            if task_update.assigned_to:
                send_task_update_email(task_update)
            return redirect("task_list")
        return render(
            request, self.template_name, {"form": form, "task": task}
        )


class DeleteTaskView(TemplateView):
    """
    View to delete a task.
    """

    def post(self, request, pk):
        """
        Handle task deletion.
        """
        task = Task.objects.filter(id=pk).first()
        task.delete()
        return redirect("task_list")


class DetailTaskView(TemplateView):
    """
    View to display details of a specific task.
    """

    template_name = "task_detail.html"

    def get(self, request, pk):
        """
        Display the task details and associated comments.
        """
        task = Task.objects.get(id=pk)
        comments = Comment.objects.filter(task=task)
        form = CommentForm()
        context = {"task": task, "comments": comments, "form": form}
        return render(request, self.template_name, context=context)

    def post(self, request, pk):
        """
        Add a new comment to the task.
        """
        task = Task.objects.get(id=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.task = task
            comment.save()
            return redirect("task_list")
        comments = Comment.objects.filter(task=task)
        context = {"task": task, "comments": comments, "form": form}
        return render(request, self.template_name, context)


class TaskListView(TemplateView):
    """
    View to display a list of tasks with optional filtering.
    """

    template_name = "task_list.html"

    def get(self, request):
        """
        Display the task list with filters for assigned user, status, and due date.
        """
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
    """
    View to display a list of users.
    """

    template_name = "user_list.html"

    def get(self, request):
        """
        Display all users.
        """
        user = User.objects.all()
        context = {"user": user}
        return render(request, self.template_name, context=context)


class TaskStatusUpdateView(TemplateView):
    """
    View to update the status of a task.
    """

    template_name = "status_update.html"

    def get(self, request, pk):
        """
        Render the task status update form.
        """
        task = Task.objects.filter(id=pk).first()
        form = TaskStatusForm(instance=task)
        return render(
            request, self.template_name, {"form": form, "task": task}
        )

    def post(self, request, pk):
        """
        Process the task status update form.
        """
        task = Task.objects.filter(id=pk).first()
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_list")
        return render(
            request, self.template_name, {"form": form, "task": task}
        )
