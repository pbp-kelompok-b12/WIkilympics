from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from article.models import Article

# # Create your tests here.
class ArticleTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.normal_user = User.objects.create_user(username='testuser', password='testpassword')
        User.objects.create_user(username='admin', password='adminpassword', is_staff=True) # Admin user for completeness

        # Setup Articles
        self.article1 = Article.objects.create(
            title='Article 1 Normal', content='Content 1.', category='athletics', thumbnail='http://example.com/img1.jpg',
        )
        self.article2 = Article.objects.create(
            title='Article 2 Trending', content='Content 2.', category='swimming', thumbnail='http://example.com/img2.jpg',
        )
        # Membuat article2 trending (like_count > 6)
        for i in range(7):
            self.article2.like_user.add(User.objects.create_user(username=f'liker{i}', password='pw'))

        # Setup URLs
        self.urls = {
            'show': reverse('article:show_articles'),
            'json': reverse('article:show_json'),
            'json_id': reverse('article:show_json_id', kwargs={'article_id': self.article1.id}),
            'add': reverse('article:add_article'),
            'edit': reverse('article:edit_article', kwargs={'id': self.article1.id}),
            'delete': reverse('article:delete_article', kwargs={'id': self.article1.id}),
            'detail': reverse('article:article_detail', kwargs={'id': self.article1.id}),
            'like': reverse('article:like_article', kwargs={'article_id': self.article1.id}),
            'dislike': reverse('article:dislike_article', kwargs={'article_id': self.article1.id}),
        }
        
        self.new_data = {
            'title': 'New Title', 'content': 'New Content', 'category': 'a', 'thumbnail': 'http://new.com/img.jpg'
        }

    def test_show_articles_view(self):
        response = self.client.get(self.urls['show'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_articles.html')

    def test_json_views(self):
        self.client.login(username='testuser', password='testpassword')
        self.article1.like_user.add(self.normal_user)
        
        # Test show_json (Mencakup is_liked/is_disliked path)
        response_json = self.client.get(self.urls['json']).json()
        article_data = next(a for a in response_json if a['id'] == str(self.article1.id))
        self.assertTrue(article_data['is_liked'])
        
        # Test show_json_id (Success)
        response_json_id = self.client.get(self.urls['json_id'])
        self.assertEqual(response_json_id.status_code, 200)
        self.assertEqual(response_json_id.json()['title'], 'Article 1 Normal')
        
        # Test show_json_id (404)
        non_existent_id = '00000000-0000-0000-0000-000000000000'
        url_404_json = reverse('article:show_json_id', kwargs={'article_id': non_existent_id})
        self.assertEqual(self.client.get(url_404_json).status_code, 404)

    def test_article_crud_flow(self):
        initial_count = Article.objects.count()

        # add
        self.assertEqual(self.client.post(self.urls['add'], self.new_data).status_code, 200)
        self.assertEqual(Article.objects.count(), initial_count + 1)
        
        # edit
        updated_data = self.new_data.copy()
        updated_data['title'] = 'Updated Title'
        self.assertEqual(self.client.post(self.urls['edit'], updated_data).status_code, 200)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, 'Updated Title')
        
        # delete
        self.assertEqual(self.client.post(self.urls['delete']).status_code, 200)
        self.assertEqual(Article.objects.count(), initial_count)

    def test_article_detail_view(self):
        # Success path
        response = self.client.get(self.urls['detail'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'article_detail.html')

        # 404
        non_existent_id = '00000000-0000-0000-0000-000000000000'
        url_404_detail = reverse('article:article_detail', kwargs={'id': non_existent_id})
        self.assertEqual(self.client.get(url_404_detail).status_code, 404)
        
        # Models: __str__, like_count, is_trending
        self.assertEqual(str(self.article1), 'Article 1 Normal')
        self.assertEqual(self.article1.like_count, 0)
        self.assertFalse(self.article1.is_trending)
        self.assertTrue(self.article2.is_trending)

    # User react ketika login
    def test_reactions_requires_login(self):
        self.assertEqual(self.client.get(self.urls['like']).status_code, 302)
        self.assertEqual(self.client.get(self.urls['dislike']).status_code, 302)

    # Like dislike
    def test_reactions_logic_full(self):
        self.client.login(username='testuser', password='testpassword')
        
        # like
        self.client.post(self.urls['like'])
        self.article1.refresh_from_db()
        self.assertTrue(self.article1.like_user.exists())
        self.assertEqual(self.article1.like_count, 1)

        # dislike (hapus like sebelum)
        self.client.post(self.urls['dislike'])
        self.article1.refresh_from_db()
        self.assertFalse(self.article1.like_user.exists())
        self.assertTrue(self.article1.dislike_user.exists())

        # like (hapus dislike sebelum)
        response_like_toggle = self.client.post(self.urls['like'])
        self.article1.refresh_from_db()
        self.assertTrue(self.article1.like_user.exists())
        self.assertFalse(self.article1.dislike_user.exists())
        self.assertEqual(response_like_toggle.json()['likes'], 1)

        # like (hapus like)
        self.client.post(self.urls['like'])
        self.article1.refresh_from_db()
        self.assertFalse(self.article1.like_user.exists())

        # dislike (hapus dislike)
        self.client.post(self.urls['dislike']) 
        self.client.post(self.urls['dislike']) 
        self.article1.refresh_from_db()
        self.assertFalse(self.article1.dislike_user.exists())