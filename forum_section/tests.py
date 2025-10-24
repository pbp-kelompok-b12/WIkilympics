from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Forum, Discussion
from .forms import ForumForm, DiscussionForm
import json


class ForumModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description',
            thumbnail='https://example.com/image.jpg'
        )
    
    def test_forum_creation(self):
        self.assertEqual(self.forum.topic, 'Test Forum')
        self.assertEqual(self.forum.name, self.user)
        self.assertEqual(str(self.forum), 'Test Forum')
    
    def test_forum_thumbnail_optional(self):
        forum = Forum.objects.create(
            name=self.user,
            topic='Forum Without Thumbnail',
            description='No image'
        )
        self.assertEqual(forum.thumbnail, '')


class DiscussionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
        self.discussion = Discussion.objects.create(
            username=self.user,
            forum=self.forum,
            discuss='Test discussion content'
        )
    
    def test_discussion_creation(self):
        self.assertEqual(self.discussion.discuss, 'Test discussion content')
        self.assertEqual(self.discussion.username, self.user)
        self.assertEqual(self.discussion.forum, self.forum)
        self.assertEqual(str(self.discussion), 'Test Forum')


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
        self.discussion = Discussion.objects.create(
            username=self.user,
            forum=self.forum,
            discuss='Test discussion'
        )
    
    def test_home_view_requires_login(self):
        response = self.client.get(reverse('forum_section:home'))
        self.assertEqual(response.status_code, 302)
    
    def test_home_view_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('forums', response.context)
        self.assertIn('count', response.context)
        self.assertIn('discussions', response.context)
        self.assertEqual(response.context['count'], 1)


class EditForumViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
    
    def test_edit_forum_requires_login(self):
        response = self.client.get(reverse('forum_section:edit_forum', args=[self.forum.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_edit_forum_owner_can_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:edit_forum', args=[self.forum.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editForum.html')
    
    def test_edit_forum_non_owner_redirected(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('forum_section:edit_forum', args=[self.forum.id]))
        self.assertRedirects(response, reverse('forum_section:home'))
    
    def test_edit_forum_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('forum_section:edit_forum', args=[self.forum.id]), {
            'topic': 'Updated Forum',
            'description': 'Updated Description',
            'thumbnail': 'https://example.com/new.jpg'
        })
        self.forum.refresh_from_db()
        self.assertEqual(self.forum.topic, 'Updated Forum')
        self.assertRedirects(response, reverse('forum_section:home'))


class EditDiscussionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
        self.discussion = Discussion.objects.create(
            username=self.user,
            forum=self.forum,
            discuss='Test discussion'
        )
    
    def test_edit_discussion_requires_login(self):
        response = self.client.get(reverse('forum_section:edit_discussion', args=[self.discussion.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_edit_discussion_owner_can_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:edit_discussion', args=[self.discussion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editDiscussion.html')


class AddInForumViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_add_forum_requires_login(self):
        response = self.client.get(reverse('forum_section:addInForum'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_forum_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:addInForum'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addInForum.html')
    
    def test_add_forum_ajax_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forum_section:addInForum'),
            {
                'topic': 'New Forum',
                'description': 'New Description',
                'thumbnail': 'https://example.com/image.jpg'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(Forum.objects.count(), 1)


class AddInDiscussionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
    
    def test_add_discussion_requires_login(self):
        response = self.client.get(reverse('forum_section:addInDiscussion', args=[self.forum.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_add_discussion_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:addInDiscussion', args=[self.forum.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addInDiscussion.html')
    
    def test_add_discussion_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('forum_section:addInDiscussion', args=[self.forum.id]),
            {
                'forum': self.forum.id,
                'discuss': 'New discussion content'
            }
        )
        self.assertEqual(Discussion.objects.count(), 1)
        self.assertRedirects(response, reverse('forum_section:home'))


class DeleteForumViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
    
    def test_delete_forum_requires_login(self):
        response = self.client.post(reverse('forum_section:delete_forum', args=[self.forum.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_delete_forum_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('forum_section:delete_forum', args=[self.forum.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(Forum.objects.count(), 0)


class DeleteDiscussionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
        self.discussion = Discussion.objects.create(
            username=self.user,
            forum=self.forum,
            discuss='Test discussion'
        )
    
    def test_delete_discussion_requires_login(self):
        response = self.client.post(reverse('forum_section:delete_discussion', args=[self.discussion.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_delete_discussion_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('forum_section:delete_discussion', args=[self.discussion.id]))
        self.assertRedirects(response, reverse('forum_section:home'))
        self.assertEqual(Discussion.objects.count(), 0)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_register_get(self):
        response = self.client.get(reverse('forum_section:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_register_post_valid(self):
        response = self.client.post(reverse('forum_section:register'), {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertRedirects(response, reverse('forum_section:login'))


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_login_get(self):
        response = self.client.get(reverse('forum_section:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_login_post_valid(self):
        response = self.client.post(reverse('forum_section:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('forum_section:show_main'))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forum_section:logout'))
        self.assertRedirects(response, reverse('forum_section:login'))


class ForumFormTest(TestCase):
    def test_forum_form_valid(self):
        form = ForumForm(data={
            'topic': 'Test Topic',
            'description': 'Test Description',
            'thumbnail': 'https://example.com/image.jpg'
        })
        self.assertTrue(form.is_valid())
    
    def test_forum_form_invalid_missing_topic(self):
        form = ForumForm(data={
            'description': 'Test Description'
        })
        self.assertFalse(form.is_valid())


class DiscussionFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(
            name=self.user,
            topic='Test Forum',
            description='Test Description'
        )
    
    def test_discussion_form_valid(self):
        form = DiscussionForm(data={
            'forum': self.forum.id,
            'discuss': 'Test discussion'
        })
        self.assertTrue(form.is_valid())
    
    def test_discussion_form_invalid_missing_discuss(self):
        form = DiscussionForm(data={
            'forum': self.forum.id
        })
        self.assertFalse(form.is_valid())
