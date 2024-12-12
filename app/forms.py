from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Comment, Task, User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=200, required=True)

    class Meta:
        fields = ["username", "password"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "detail",
            "due_date",
            "status",
            "priority",
            "assigned_to",
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class TaskStatusForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ["status"]
