from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    CreateTaskView,
    DeleteTaskView,
    DetailTaskView,
    Home,
    LoginView,
    LogoutView,
    SignUpView,
    TaskListView,
    TaskStatusUpdateView,
    UpdateTaskView,
    UserListView,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/task/", CreateTaskView.as_view(), name="create_task"),
    path("list/task/", TaskListView.as_view(), name="task_list"),
    path(
        "taskdetail/task/<int:pk>/",
        DetailTaskView.as_view(),
        name="detail_task",
    ),
    path(
        "taskupdate/task/<int:pk>/", UpdateTaskView.as_view(), name="edit_task"
    ),
    path(
        "delete/task/<int:task_id>",
        DeleteTaskView.as_view(),
        name="delete_task",
    ),
    path("userlist/", UserListView.as_view(), name="user_list"),
    path(
        "update/status/<int:pk>/",
        TaskStatusUpdateView.as_view(),
        name="status_update",
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
