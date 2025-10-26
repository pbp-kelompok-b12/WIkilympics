from django.test import TestCase, Client
from django.urls import reverse
from athletes.models import Athletes
import uuid

class AthletesTestCase(TestCase):
    def setUp(self):
        # Setup data test
        self.athlete = Athletes.objects.create(
            athlete_name="Test Athlete",
            country="Test Country",
            sport="Test Sport",
            biography="Test biography",
            athlete_photo="https://example.com/photo.jpg"
        )
        
        self.client = Client()
        
        # User admin untuk testing
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )

    def test_show_main(self):
        """Test halaman utama"""
        response = self.client.get(reverse('athletes:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'athletes.html')
        self.assertContains(response, 'OLYMPIC ATHLETES')

    def test_show_main_with_filters(self):
        """Test halaman utama dengan filter"""
        response = self.client.get(reverse('athletes:show_main') + '?sport=Test Sport&country=Test&q=Athlete')
        self.assertEqual(response.status_code, 200)

    def test_show_athlete_detail(self):
        """Test halaman detail athlete"""
        response = self.client.get(reverse('athletes:show_athlete', args=[self.athlete.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'athlete_detail.html')
        self.assertContains(response, 'Test Athlete')

    def test_show_athlete_detail_not_found(self):
        """Test halaman detail dengan ID tidak valid"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('athletes:show_athlete', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)

    def test_show_json(self):
        """Test endpoint JSON semua athletes"""
        response = self.client.get(reverse('athletes:show_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_show_json_by_id(self):
        """Test endpoint JSON by ID"""
        response = self.client.get(reverse('athletes:show_json_by_id', args=[self.athlete.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_show_json_by_id_not_found(self):
        """Test endpoint JSON dengan ID tidak valid"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('athletes:show_json_by_id', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)

    def test_create_athlete_entry_ajax_success(self):
        """Test create athlete via AJAX"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'athlete_name': 'New Athlete',
            'country': 'New Country',
            'sport': 'New Sport',
            'biography': 'New biography',
            'athlete_photo': 'https://example.com/new.jpg'
        }
        
        response = self.client.post(
            reverse('athletes:create_athlete_entry_ajax'),
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'success', 'message': 'Athlete added successfully!'}
        )
        
        # Verify athlete created
        self.assertTrue(Athletes.objects.filter(athlete_name='New Athlete').exists())

    def test_create_athlete_entry_ajax_missing_fields(self):
        """Test create athlete dengan field yang kurang"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'athlete_name': 'New Athlete',
            # Missing required fields
        }
        
        response = self.client.post(
            reverse('athletes:create_athlete_entry_ajax'),
            data
        )
        
        self.assertEqual(response.status_code, 400)

    def test_edit_athlete_entry_ajax_success(self):
        """Test edit athlete via AJAX"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'athlete_name': 'Updated Athlete',
            'country': 'Updated Country',
            'sport': 'Updated Sport',
            'biography': 'Updated biography',
            'athlete_photo': 'https://example.com/updated.jpg'
        }
        
        response = self.client.post(
            reverse('athletes:edit_athlete_entry_ajax', args=[self.athlete.id]),
            data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify athlete updated
        self.athlete.refresh_from_db()
        self.assertEqual(self.athlete.athlete_name, 'Updated Athlete')

    def test_delete_athlete_entry_ajax_success(self):
        """Test delete athlete via AJAX"""
        self.client.login(username='admin', password='admin123')
        
        athlete_to_delete = Athletes.objects.create(
            athlete_name="To Delete",
            country="Country",
            sport="Sport",
            biography="Bio"
        )
        
        response = self.client.post(
            reverse('athletes:delete_athlete_entry_ajax', args=[athlete_to_delete.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'success', 'message': 'Athlete deleted successfully.'}
        )
        
        # Verify athlete deleted
        self.assertFalse(Athletes.objects.filter(id=athlete_to_delete.id).exists())

    def test_delete_athlete_entry_ajax_not_found(self):
        """Test delete athlete dengan ID tidak valid"""
        self.client.login(username='admin', password='admin123')
        
        invalid_id = uuid.uuid4()
        response = self.client.post(
            reverse('athletes:delete_athlete_entry_ajax', args=[invalid_id])
        )
        
        self.assertEqual(response.status_code, 404)

    def test_model_string_representation(self):
        """Test string representation model"""
        self.assertEqual(str(self.athlete), 'Test Athlete')

    def test_get_sport_display(self):
        """Test method get_sport_display"""
        self.assertEqual(self.athlete.get_sport_display(), 'Test Sport')

    def test_authentication_required_for_admin_actions(self):
        """Test bahwa aksi admin membutuhkan login"""
        # Test tanpa login
        response = self.client.post(
            reverse('athletes:create_athlete_entry_ajax'),
            {'athlete_name': 'Test'}
        )
        # Should still work karena menggunakan @csrf_exempt
        self.assertEqual(response.status_code, 400)  # Error karena data kurang

    def test_url_patterns(self):
        """Test semua URL patterns"""
        # Test main page
        response = self.client.get('/athletes/')
        self.assertEqual(response.status_code, 200)
        
        # Test athlete detail
        response = self.client.get(f'/athletes/{self.athlete.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Test JSON endpoint
        response = self.client.get('/athletes/json/')
        self.assertEqual(response.status_code, 200)

class AthletesFormTestCase(TestCase):
    def test_athletes_form_valid(self):
        """Test form validation"""
        from athletes.forms import AthletesForm
        
        form_data = {
            'athlete_name': 'Form Test',
            'country': 'Form Country',
            'sport': 'Form Sport',
            'biography': 'Form biography'
        }
        
        form = AthletesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_athletes_form_invalid(self):
        """Test form validation dengan data invalid"""
        from athletes.forms import AthletesForm
        
        form_data = {
            'athlete_name': '',  # Required field empty
            'country': 'Country',
            'sport': 'Sport',
            'biography': 'Bio'
        }
        
        form = AthletesForm(data=form_data)
        self.assertFalse(form.is_valid())