from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import PollQuestion, PollOption
from .forms import PollForm
from . import views


class PollModelTest(TestCase):
    def setUp(self):
        self.question = PollQuestion.objects.create(question_text="Siapa pemain favoritmu?")
        self.option1 = PollOption.objects.create(question=self.question, option_text="Messi", votes=3)
        self.option2 = PollOption.objects.create(question=self.question, option_text="Ronaldo", votes=2)

    def test_str_methods(self):
        self.assertEqual(str(self.question), "Siapa pemain favoritmu?")
        self.assertEqual(str(self.option1), "Messi")

    def test_total_votes(self):
        self.assertEqual(self.question.total_votes(), 5)


class PollFormTest(TestCase):
    def test_valid_form(self):
        form = PollForm(data={"question_text": "Apa warna favoritmu?"})
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = PollForm(data={"question_text": ""})
        self.assertFalse(form.is_valid())


class LandingPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("landingpoll:landing_page")
        self.admin_user = User.objects.create_superuser("admin", "admin@example.com", "adminpass")
        self.normal_user = User.objects.create_user("user", "user@example.com", "userpass")

    def test_landing_page_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")

    def test_add_poll_post_as_admin(self):
        self.client.login(username="admin", password="adminpass")
        data = {
            "add_poll": "1",
            "question": "Pertanyaan tes?",
            "options[]": ["A", "B", "C"]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PollQuestion.objects.filter(question_text="Pertanyaan tes?").exists())

    def test_add_poll_ajax(self):
        self.client.login(username="admin", password="adminpass")
        data = {
            "add_poll": "1",
            "question": "Tes AJAX",
            "options[]": ["X", "Y"]
        }
        response = self.client.post(
            self.url, data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            response.json()
        )
        self.assertIn("status", response.json())

    def test_save_edit_poll_as_admin(self):
        self.client.login(username="admin", password="adminpass")
        poll = PollQuestion.objects.create(question_text="Lama")
        data = {
            "save_edit": "1",
            "poll_id": poll.id,
            "question": "Baru",
            "options[]": ["1", "2"]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        poll.refresh_from_db()
        self.assertEqual(poll.question_text, "Baru")

    def test_save_edit_poll_ajax(self):
        self.client.login(username="admin", password="adminpass")
        poll = PollQuestion.objects.create(question_text="Old")
        data = {
            "save_edit": "1",
            "poll_id": poll.id,
            "question": "Updated",
            "options[]": ["A", "B"]
        }
        response = self.client.post(
            self.url, data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_post_as_non_admin(self):
        self.client.login(username="user", password="userpass")
        data = {"add_poll": "1", "question": "Tes", "options[]": ["A", "B"]}
        response = self.client.post(self.url, data)
        # Non-admin tidak bisa menambahkan polling
        self.assertEqual(response.status_code, 200)  # tetap render halaman
        self.assertFalse(PollQuestion.objects.exists())


class DeletePollViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser("admin", "admin@example.com", "adminpass")
        self.normal_user = User.objects.create_user("user", "user@example.com", "userpass")
        self.poll = PollQuestion.objects.create(question_text="Hapus saya")

    def test_delete_poll_as_admin(self):
        self.client.login(username="admin", password="adminpass")
        url = reverse("landingpoll:delete_poll", args=[self.poll.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PollQuestion.objects.filter(id=self.poll.id).exists())

    def test_delete_poll_ajax(self):
        self.client.login(username="admin", password="adminpass")
        url = reverse("landingpoll:delete_poll", args=[self.poll.id])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), response.json())

    def test_delete_poll_non_admin(self):
        self.client.login(username="user", password="userpass")
        url = reverse("landingpoll:delete_poll", args=[self.poll.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class VotePollViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = PollQuestion.objects.create(question_text="Siapa presiden?")
        self.option = PollOption.objects.create(question=self.poll, option_text="A", votes=1)

    def test_vote_poll(self):
        url = reverse("landingpoll:vote_poll", args=[self.option.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.option.refresh_from_db()
        self.assertEqual(self.option.votes, 2)
        self.assertEqual(response.json()["success"], True)
        self.assertIn("total_votes", response.json())


class URLConfTest(TestCase):
    def test_urls_resolve_correctly(self):
        self.assertEqual(resolve("/").func, views.landing_page)
        self.assertEqual(resolve("/vote/1/").func, views.vote_poll)
        self.assertEqual(resolve("/delete/1/").func, views.delete_poll)
