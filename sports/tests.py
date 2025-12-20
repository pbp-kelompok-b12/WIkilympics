from django.test import TestCase, Client
from django.urls import reverse, resolve
from sports.models import Sports
from sports.views import show_main, show_sport, show_json, show_json_by_id, create_sport_entry_ajax, edit_sport_entry_ajax, delete_sport_entry_ajax
from django.http import JsonResponse
import json

# ==============================================================================
# Model Tests
# ==============================================================================
class SportsModelTest(TestCase):
    """
    Menguji model Sports.
    """
    def setUp(self):
        """Siapkan objek Sports untuk pengujian."""
        self.sport = Sports.objects.create(
            sport_name="Sepak Bola",
            sport_description="Olahraga tim yang dimainkan dengan bola.",
            participation_structure='team',
            sport_type='athletic_sport',
            country_of_origin='Inggris',
            first_year_played=1863,
            history_description='Sejarah panjang...',
            equipment='Bola, gawang, sepatu'
        )

    def test_sports_creation(self):
        """Memastikan objek Sports dibuat dengan benar."""
        self.assertTrue(isinstance(self.sport, Sports))
        self.assertEqual(self.sport.__str__(), "Sepak Bola")
        self.assertEqual(self.sport.sport_name, "Sepak Bola")
        self.assertIsNotNone(self.sport.id)
        self.assertEqual(self.sport.first_year_played, 1863)

    def test_default_values(self):
        """Memastikan nilai default diterapkan dengan benar."""
        default_sport = Sports.objects.create(
            sport_name="Default Sport",
            sport_description="Desc",
            country_of_origin="Country",
            history_description="History",
            equipment="Equipment"
        )
        self.assertEqual(default_sport.participation_structure, 'individual')
        self.assertEqual(default_sport.sport_type, 'athletic_sport')
        self.assertEqual(default_sport.first_year_played, 0)
        self.assertIsNone(default_sport.sport_img)

# ----------------------------------------------------------------------

# ==============================================================================
# URL Tests
# ==============================================================================
class SportsURLTest(TestCase):
    """
    Menguji resolusi URL ke view yang benar.
    """
    def test_show_main_url_resolves(self):
        url = reverse('sports:show_main')
        self.assertEqual(resolve(url).func, show_main)

    def test_show_sport_url_resolves(self):
        url = reverse('sports:show_sport', args=['12345678-1234-5678-1234-567812345678'])
        self.assertEqual(resolve(url).func, show_sport)

    def test_show_json_url_resolves(self):
        url = reverse('sports:show_json')
        self.assertEqual(resolve(url).func, show_json)

    def test_show_json_by_id_url_resolves(self):
        url = reverse('sports:show_json_by_id', args=['1'])
        self.assertEqual(resolve(url).func, show_json_by_id)

    def test_create_sport_entry_ajax_url_resolves(self):
        url = reverse('sports:create_sport_entry_ajax')
        self.assertEqual(resolve(url).func, create_sport_entry_ajax)

    def test_edit_sport_entry_ajax_url_resolves(self):
        uuid_str = 'a1b2c3d4-a1b2-c3d4-a1b2-c3d4a1b2c3d4'
        url = reverse('sports:edit_sport_entry_ajax', args=[uuid_str])
        self.assertEqual(resolve(url).func, edit_sport_entry_ajax)

    def test_delete_sport_entry_ajax_url_resolves(self):
        uuid_str = 'a1b2c3d4-a1b2-c3d4-a1b2-c3d4a1b2c3d4'
        url = reverse('sports:delete_sport_entry_ajax', args=[uuid_str])
        self.assertEqual(resolve(url).func, delete_sport_entry_ajax)

# ----------------------------------------------------------------------

# ==============================================================================
# View Tests
# ==============================================================================
class SportsViewTest(TestCase):
    """
    Menguji fungsi-fungsi view di views.py.
    """
    def setUp(self):
        """Siapkan Client dan beberapa objek Sports untuk pengujian."""
        self.client = Client()
        self.sport1 = Sports.objects.create(
            sport_name="Renang",
            sport_description="Sport air",
            participation_structure='individual',
            sport_type='water_sport',
            country_of_origin='Yunani Kuno',
            first_year_played=1896,
            history_description='Sejarah renang...',
            equipment='Pakaian renang'
        )
        self.sport2 = Sports.objects.create(
            sport_name="Angkat Besi",
            sport_description="Sport kekuatan",
            participation_structure='individual',
            sport_type='strength_sport',
            country_of_origin='Eropa',
            first_year_played=1891,
            history_description='Sejarah angkat besi...',
            equipment='Barbel'
        )
        self.sport3 = Sports.objects.create(
            sport_name="Bulu Tangkis",
            sport_description="Sport raket",
            participation_structure='both',
            sport_type='racket_sport',
            country_of_origin='India',
            first_year_played=1873,
            history_description='Sejarah bulu tangkis...',
            equipment='Raket, kok'
        )
        self.non_existent_uuid = '99999999-9999-9999-9999-999999999999'

    # ------------------
    # show_main Tests
    # ------------------
    # ... (Test show_main tetap sama)

    def test_show_main_uses_correct_template(self):
        """Memastikan show_main menggunakan template yang benar."""
        response = self.client.get(reverse('sports:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports.html')

    def test_show_main_displays_all_sports(self):
        """Memastikan show_main menampilkan semua objek Sports."""
        response = self.client.get(reverse('sports:show_main'))
        self.assertEqual(len(response.context['sports_list']), 3)

    def test_show_main_filter_by_category(self):
        """Memastikan filter berdasarkan sport_type berfungsi."""
        url = reverse('sports:show_main') + '?category=water_sport'
        response = self.client.get(url)
        self.assertEqual(len(response.context['sports_list']), 1)
        self.assertEqual(response.context['sports_list'][0].sport_name, "Renang")

    def test_show_main_filter_by_participation(self):
        """Memastikan filter berdasarkan participation_structure berfungsi."""
        url = reverse('sports:show_main') + '?participation=both'
        response = self.client.get(url)
        self.assertEqual(len(response.context['sports_list']), 1)

    def test_show_main_search_by_query(self):
        """Memastikan pencarian berdasarkan sport_name berfungsi."""
        url = reverse('sports:show_main') + '?q=Ren' 
        response = self.client.get(url)
        self.assertEqual(len(response.context['sports_list']), 1)
        self.assertEqual(response.context['sports_list'][0].sport_name, "Renang")

    # ------------------
    # show_sport Tests
    # ------------------
    def test_show_sport_exists(self):
        """Memastikan show_sport menampilkan detail olahraga yang ada."""
        url = reverse('sports:show_sport', args=[str(self.sport1.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_show_sport_not_exists(self):
        """Memastikan show_sport melempar 404 jika olahraga tidak ditemukan."""
        url = reverse('sports:show_sport', args=[self.non_existent_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    # ------------------
    # show_json Tests
    # ------------------
    def test_show_json(self):
        """Memastikan show_json mengembalikan data JSON dari semua Sports."""
        response = self.client.get(reverse('sports:show_json'))
        self.assertEqual(response.status_code, 200)

    def test_show_json_by_id_exists(self):
        """Memastikan show_json_by_id mengembalikan data JSON Sports yang benar."""
        response = self.client.get(reverse('sports:show_json_by_id', args=[self.sport1.id]))
        self.assertEqual(response.status_code, 200)

    def test_show_json_by_id_not_exists(self):
        """Memastikan show_json_by_id mengembalikan 404 jika tidak ditemukan."""
        response = self.client.get(reverse('sports:show_json_by_id', args=[self.non_existent_uuid]))
        self.assertEqual(response.status_code, 404)
        
    # ------------------
    # create_sport_entry_ajax Tests
    # ------------------
    def test_create_sport_entry_ajax_success(self):
        """Memastikan create_sport_entry_ajax berhasil membuat Sports baru."""
        initial_count = Sports.objects.count()
        post_data = {
            'sport_name': 'Basket',
            'sport_description': 'Sport bola basket',
            'participation_structure': 'team',
            'sport_type': 'athletic_sport',
            'country_of_origin': 'AS',
            'first_year_played': 1891,
            'history_description': 'Sejarah Basket',
            'equipment': 'Bola basket, ring'
        }
        url = reverse('sports:create_sport_entry_ajax')
        response = self.client.post(url, post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Sports.objects.count(), initial_count + 1)

    # ------------------------------------------------------------------
    # TAMBAHAN: edit_sport_entry_ajax Tests (Lengkap)
    # ------------------------------------------------------------------
    def test_edit_sport_entry_ajax_post_success(self):
        """Memastikan POST berhasil memperbarui Sports."""
        url = reverse('sports:edit_sport_entry_ajax', args=[self.sport2.id])
        updated_data = {
            'sport_name': 'Angkat Besi Modern',
            'sport_description': self.sport2.sport_description,
            'participation_structure': self.sport2.participation_structure,
            'sport_type': self.sport2.sport_type,
            'country_of_origin': self.sport2.country_of_origin,
            'first_year_played': self.sport2.first_year_played,
            'history_description': self.sport2.history_description,
            'equipment': self.sport2.equipment,
        }
        response = self.client.post(url, updated_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.sport2.refresh_from_db()
        self.assertEqual(self.sport2.sport_name, 'Angkat Besi Modern')

    def test_edit_sport_entry_ajax_invalid_data(self):
        """Menguji kegagalan POST karena data tidak valid (Mencakup baris 141-142)."""
        url = reverse('sports:edit_sport_entry_ajax', args=[self.sport2.id])
        # Mengirim data yang melanggar batasan model (misalnya, sport_name kosong jika CharField kosong=False)
        invalid_data = {
            'sport_name': '', # Harus gagal validasi
            'sport_description': self.sport2.sport_description,
            'participation_structure': self.sport2.participation_structure,
            'sport_type': self.sport2.sport_type,
            'country_of_origin': self.sport2.country_of_origin,
            'first_year_played': self.sport2.first_year_played,
            'history_description': self.sport2.history_description,
            'equipment': self.sport2.equipment,
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('sport_name', data['errors'])

    def test_edit_sport_entry_ajax_not_found(self):
        """Menguji kegagalan POST jika Sports tidak ditemukan (404)."""
        url = reverse('sports:edit_sport_entry_ajax', args=[self.non_existent_uuid])
        valid_data = {
            'sport_name': 'Test', 'sport_description': 'D', 'participation_structure': 'team', 
            'sport_type': 'athletic_sport', 'country_of_origin': 'C', 'first_year_played': 2000, 
            'history_description': 'H', 'equipment': 'E',
        }
        # Gunakan get_object_or_404, ini harus melempar 404
        response = self.client.post(url, valid_data)
        self.assertEqual(response.status_code, 404)

    def test_edit_sport_entry_ajax_invalid_method(self):
        """Menguji metode HTTP yang tidak diizinkan (GET) (Mencakup baris 143-144)."""
        url = reverse('sports:edit_sport_entry_ajax', args=[self.sport2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid request method.')

    # ------------------------------------------------------------------
    # TAMBAHAN: delete_sport_entry_ajax Tests (Lengkap)
    # ------------------------------------------------------------------
    def test_delete_sport_entry_ajax_post_success(self):
        """Memastikan POST berhasil menghapus Sports."""
        initial_count = Sports.objects.count()
        url = reverse('sports:delete_sport_entry_ajax', args=[self.sport3.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(Sports.objects.count(), initial_count - 1)

    def test_delete_sport_entry_ajax_not_found(self):
        """Menguji kegagalan POST jika Sports tidak ditemukan (Mencakup jalur try-except 404)."""
        url = reverse('sports:delete_sport_entry_ajax', args=[self.non_existent_uuid])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Sport not found.')

    def test_delete_sport_entry_ajax_invalid_method(self):
        """Menguji metode HTTP yang tidak diizinkan (GET) (Mencakup baris 151-153)."""
        url = reverse('sports:delete_sport_entry_ajax', args=[self.sport1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid request method.')