from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Task


class HomeViewTest(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class CreateTaskViewTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.assigned_by_user = self.User.objects.create_user(
            username="taskcreate",
            email="testuser@example.com",
            password="Str0ngPa$$w0rd!",
        )
        self.assigned_to_user = self.User.objects.create_user(
            username="taskassign",
            email="assign@gmail.com",
            password="password123",
        )
        self.url = reverse("create_task")

    def test_get_assign_task_view(self):
        data = {
            "title": "Test Task",
            "assigned_to": self.assigned_to_user.id,
            "due_date": "2024-12-31",
            "detail": "Test Task Description",
            "status": "Inprogress",
            "priority": "Major",
        }

        self.client.login(
            username="testuser@example.com", password="Str0ngPa$$w0rd!"
        )

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))

        task = Task.objects.get(title="Test Task")
        self.assertEqual(task.assigned_by, self.assigned_by_user)
        self.assertEqual(task.assigned_to, self.assigned_to_user)
        self.assertEqual(task.detail, "Test Task Description")

    def test_create_task_post_invalid(self):
        # Test invalid POST request to create a task (missing title)
        data = {
            "title": "",
            "assigned_to": self.assigned_to_user.id,
            "due_date": "2024-12-31",
            "detail": "Test Task Description",
            "status": "Inprogress",
            "priority": "Major",
        }
        self.client.login(
            username="testuser@example.com", password="Str0ngPa$$w0rd!"
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_task.html")
        self.assertTrue(response.context["form"].errors)


class TaskUpdateViewTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.assigned_by_user = self.User.objects.create_user(
            username="taskcreate",
            email="testuser@example.com",
            password="Str0ngPa$$w0rd!",
        )
        self.assigned_to_user = self.User.objects.create_user(
            username="taskassign",
            email="assign@gmail.com",
            password="password123",
        )
        self.task = Task.objects.create(
            title="Test Task",
            detail="Test Task Description",
            assigned_to=self.assigned_to_user,
            assigned_by=self.assigned_by_user,
            status="Inprogress",
            priority="Major",
            due_date="2024-12-31",
        )
        self.url = reverse("edit_task", kwargs={"pk": self.task.pk})

    def test_get_update_task(self):
        self.client.login(
            username="testuser@example.com", password="Str0ngPa$$w0rd!"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_update.html")

    def test_post_task_update_success(self):
        data = {
            "title": "Task 2",
            "detail": "Task 2 description",
            "status": "Inprogress",
            "priority": "Major",
            "assigned_to": self.assigned_to_user.id,
            "due_date": "2025-01-01",
        }
        self.client.login(username="creator@gmail.com", password="password123")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Task 2")
        self.assertEqual(self.task.detail, "Task 2 description")
        self.assertEqual(self.task.status, "Inprogress")
        self.assertEqual(self.task.priority, "Major")
        self.assertRedirects(response, reverse("task_list"))


class TaskListViewTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username="testuser1",
            email="user@gmail.com",
            password="password123",
        )
        self.user2 = self.User.objects.create_user(
            username="testuser2",
            email="user2@gmail.com",
            password="password123",
        )

        self.task1 = Task.objects.create(
            title="Task 1",
            detail="Task 1 description",
            assigned_to=self.user1,
            assigned_by=self.user2,
            status="Complete",
            priority="Major",
            due_date=date(2025, 2, 1),
        )

        self.task2 = Task.objects.create(
            title="Task 2",
            detail="Task 2 description",
            assigned_to=self.user2,
            assigned_by=self.user1,
            status="Inprogress",
            priority="Major",
            due_date=date(2025, 2, 1),
        )
        self.url = reverse("task_list")

    def test_get_request_all_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_list.html")
        self.assertEqual(len(response.context["task"]), 2)

    def test_get_request_filter_assigned_to(self):
        response = self.client.get(self.url, {"assigned_to": self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_list.html")
        self.assertEqual(len(response.context["task"]), 1)
        self.assertEqual(response.context["task"][0].assigned_to, self.user1)

    def test_get_request_filter_status(self):
        response = self.client.get(self.url, {"status": "Complete"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_list.html")
        self.assertEqual(len(response.context["task"]), 1)
        self.assertEqual(response.context["task"][0].status, "Complete")


class TaskStatusUpdateViewTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.assigned_by_user = self.User.objects.create_user(
            username="taskcreate",
            email="testuser@example.com",
            password="Str0ngPa$$w0rd!",
        )
        self.assigned_to_user = self.User.objects.create_user(
            username="taskassign",
            email="assign@gmail.com",
            password="password123",
        )
        self.task = Task.objects.create(
            title="Task 1",
            detail="Task 1 description",
            assigned_to=self.assigned_to_user,
            assigned_by=self.assigned_by_user,
            status="Inprogress",
            priority="Major",
            due_date=date(2025, 1, 1),
        )
        self.url = reverse("status_update", kwargs={"pk": self.task.pk})

    def test_get_update_task(self):
        self.client.login(
            username="testuser@example.com", password="Str0ngPa$$w0rd!"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "status_update.html")

    def test_post_task_status_update(self):
        data = {
            "status": "Complete",
        }
        self.client.login(
            username="testuser@example.com", password="Str0ngPa$$w0rd!"
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "Complete")
        self.assertRedirects(response, reverse("task_list"))
