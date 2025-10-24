from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User  # <--- ini penting
from upcoming_event.models import UpcomingEvent


# ------------------------
# TEST UNTUK SEARCH FEATURE
# ------------------------
class UpcomingEventSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.event1 = UpcomingEvent.objects.create(
            name="Jakarta Marathon",
            organizer="Jakarta Sport Org",
            date=date(2025, 11, 12),
            location="Jakarta",
            sport_branch="Running",
            description="Annual marathon event in Jakarta."
        )
        self.event2 = UpcomingEvent.objects.create(
            name="Bandung Badminton Cup",
            organizer="West Java Sports",
            date=date(2025, 12, 1),
            location="Bandung",
            sport_branch="Badminton",
            description="Regional badminton tournament."
        )

    def test_daftar_event_page_loads(self):
        """Pastikan halaman daftar_event bisa diakses"""
        response = self.client.get(reverse('upcoming_event:daftar_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upcoming_event/daftar_event.html')
        self.assertContains(response, "Upcoming Events")

    def test_search_event_by_name(self):
        """Cari event berdasarkan nama"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Marathon'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jakarta Marathon")
        self.assertNotContains(response, "Bandung Badminton Cup")

    def test_search_event_by_location(self):
        """Cari event berdasarkan lokasi"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Bandung'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bandung Badminton Cup")
        self.assertNotContains(response, "Jakarta Marathon")

    def test_search_event_by_organizer(self):
        """Cari event berdasarkan penyelenggara"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Jakarta Sport Org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jakarta Marathon")

    def test_search_no_results(self):
        """Cari event yang tidak ada hasilnya"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Swimming'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No events found")


# ------------------------
# TEST UNTUK USER AUTH
# ------------------------
class MainAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_user(self):
        """User baru bisa register"""
        response = self.client.post(reverse('main:register_user'), {
            'username': 'testuser',
            'password1': 'pass1234!',
            'password2': 'pass1234!',
        })
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_logout_flow(self):
        """Login dan logout berjalan normal"""
        user = User.objects.create_user(username='user1', password='test1234')
        # login
        response = self.client.post(reverse('main:login_user'), {
            'username': 'user1',
            'password': 'test1234'
        })
        self.assertEqual(response.status_code, 302)
        # logout
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 302)

    from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from .models import UpcomingEvent


class UpcomingEventCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )
        self.event = UpcomingEvent.objects.create(
            name="Test Event",
            organizer="Test Organizer",
            date=date(2025, 11, 1),
            location="Jakarta",
            sport_branch="Running",
            description="Test description"
        )

    def test_add_event_page_loads(self):
        """Pastikan halaman add_event bisa diakses admin"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("upcoming_event:add_event"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upcoming_event/add_event.html")

    def test_add_event_via_post(self):
        """Admin bisa menambah event baru"""
        self.client.login(username="admin", password="admin123")
        response = self.client.post(reverse("upcoming_event:add_event"), {
            "name": "Event Baru",
            "organizer": "Sport Org",
            "date": "2025-12-10",
            "location": "Bandung",
            "sport_branch": "Basketball",
            "description": "Deskripsi event baru"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UpcomingEvent.objects.filter(name="Event Baru").exists())

    def test_edit_event_page_loads(self):
        """Pastikan halaman edit_event bisa diakses admin"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("upcoming_event:edit_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upcoming_event/edit_event.html")

    def test_edit_event_via_post(self):
        """Admin bisa mengedit event"""
        self.client.login(username="admin", password="admin123")
        response = self.client.post(reverse("upcoming_event:edit_event", args=[self.event.id]), {
            "name": "Event Updated",
            "organizer": "Updated Organizer",
            "date": "2025-11-15",
            "location": "Surabaya",
            "sport_branch": "Badminton",
            "description": "Updated desc"
        })
        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Event Updated")

    def test_delete_event_via_post(self):
        """Admin bisa menghapus event"""
        self.client.login(username="admin", password="admin123")
        response = self.client.post(reverse("upcoming_event:delete_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UpcomingEvent.objects.filter(id=self.event.id).exists())

    def test_delete_event_invalid_method(self):
        """Pastikan GET ke delete_event ditolak"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("upcoming_event:delete_event", args=[self.event.id]))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid request method", response.content.decode())

