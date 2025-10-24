from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from .models import UpcomingEvent


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
        """Halaman daftar_event bisa diakses"""
        response = self.client.get(reverse('upcoming_event:daftar_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upcoming_event/daftar_event.html')
        self.assertContains(response, "Upcoming Events")

    def test_search_event_by_name(self):
        """Pencarian event berdasarkan nama"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Marathon'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jakarta Marathon")
        self.assertNotContains(response, "Bandung Badminton Cup")

    def test_search_event_by_location(self):
        """Pencarian event berdasarkan lokasi"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Bandung'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bandung Badminton Cup")
        self.assertNotContains(response, "Jakarta Marathon")

    def test_search_event_by_organizer(self):
        """Pencarian event berdasarkan organizer"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Jakarta Sport Org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jakarta Marathon")

    def test_search_no_results(self):
        """Pencarian dengan hasil kosong"""
        response = self.client.get(reverse('upcoming_event:daftar_event'), {'q': 'Swimming'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No events found")
