from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from article.models import Article
from sports.models import Sports 

class ArticleTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # 1. Buat User yang akan digunakan oleh semua test di class ini
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.admin = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')

        # 2. Buat Sport yang terdaftar
        cls.registered_sport = Sports.objects.create(sport_name='athletics')
        
        # 3. Buat Artikel untuk pengujian
        cls.article_registered = Article.objects.create(
            title='Record Lari 100m', content='Lari 100m.', category='athletics', thumbnail='http://example.com/a1.jpg'
        )
        cls.article_unregistered = Article.objects.create(
            title='E-Sports Baru', content='Artikel tentang E-Sports.', category='esports_test', thumbnail='http://example.com/a2.jpg'
        )

    def setUp(self):
        self.client = Client()

    ## 1. TEST VIEW DAN DATA JSON

    def test_show_articles_view_loads(self):
        """Test the main articles page loads successfully."""
        response = self.client.get(reverse('article:show_articles'))
        self.assertEqual(response.status_code, 200)

    def test_show_json_content(self):
        """Test JSON endpoint returns correct number of articles."""
        response = self.client.get(reverse('article:show_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        # Check anonymous status
        self.assertFalse(data[0]['is_liked'])

    def test_show_json_id_success(self):
        """Test retrieving single article data."""
        response = self.client.get(reverse('article:show_json_id', args=[self.article_registered.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Record Lari 100m')

    ## 2. TEST CRUD (ADMIN)

    def test_add_article_success(self):
        """Test adding new article."""
        self.assertEqual(Article.objects.count(), 2) # Awal
        response = self.client.post(reverse('article:add_article'), {
            'title': 'Test Add', 'content': 'Content', 'category': 'badminton', 'thumbnail': 'http://new.com/img.jpg',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Article.objects.count(), 3) # Bertambah

    def test_edit_article_success(self):
        """Test editing an existing article by POST."""
        self.client.login(username='admin', password='adminpassword')
        new_title = "TITLE BARU"
        response = self.client.post(reverse('article:edit_article', args=[self.article_registered.id]), {
            'title': new_title, 'content': self.article_registered.content, 
            'category': self.article_registered.category, 'thumbnail': self.article_registered.thumbnail,
        })
        self.assertEqual(response.status_code, 200)
        self.article_registered.refresh_from_db()
        self.assertEqual(self.article_registered.title, new_title)

    def test_delete_article_success(self):
        """Test deleting article by admin."""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(reverse('article:delete_article', args=[self.article_registered.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 1)


    ## 3. TEST LIKE/DISLIKE (Otorisasi)

    def test_like_article_unauthenticated_fails(self):
        """Test like action fails for unauthenticated user (403)."""
        response = self.client.post(reverse('article:like_article', args=[self.article_registered.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_like_article_authenticated_success(self):
        """Test liking an article works and updates count."""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('article:like_article', args=[self.article_registered.id]))
        self.article_registered.refresh_from_db()
        self.assertEqual(self.article_registered.like_count, 1)

    def test_dislike_article_switch_from_like(self):
        """Test switching from like to dislike."""
        self.client.login(username='testuser', password='password')
        # Like dulu
        self.article_registered.like_user.add(self.user)
        # Dislike
        response = self.client.post(reverse('article:dislike_article', args=[self.article_registered.id]))
        self.article_registered.refresh_from_db()
        self.assertEqual(self.article_registered.like_count, 0)
        self.assertTrue(self.article_registered.dislike_user.filter(id=self.user.id).exists())


    ## 4. TEST article_detail VIEW (Logika Kategori/Sport)

    def test_article_detail_unauthenticated_redirect(self):
        """Test unauthenticated user is redirected."""
        response = self.client.get(reverse('article:article_detail', args=[self.article_registered.id]))
        self.assertRedirects(response, reverse('article:show_articles'), status_code=302, target_status_code=200)

    def test_article_detail_sport_found_context(self):
        """Test context when Sport is registered."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('article:article_detail', args=[self.article_registered.id]))
        
        self.assertIsNotNone(response.context['sport_id'])
        self.assertEqual(response.context['sport_id'], str(self.registered_sport.id))
        self.assertEqual(response.context['clean_category_name'], 'Athletics')

    def test_article_detail_sport_not_found_context(self):
        """Test context when Sport is NOT registered (sport_id must be None)."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('article:article_detail', args=[self.article_unregistered.id]))
        
        self.assertIsNone(response.context['sport_id'])
        self.assertEqual(response.context['clean_category_name'], 'Esports Test')