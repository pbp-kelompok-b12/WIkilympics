from django.urls import path
from .views import *
from django.contrib import admin
app_name = 'forum_section'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', show_main, name = 'show_main'),
    path('forums/',home,name='home'),
    path('add-forum/',addInForum,name='addInForum'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('forum/<int:id>/add-discussion/', addInDiscussion, name='addInDiscussion'),
    path('forum/delete/<int:id>/', delete_forum, name='delete_forum'),
    path('discussion/delete/<int:id>/', delete_discussion, name='delete_discussion'),
    path('forum/edit/<int:id>/', edit_forum, name='edit_forum'),
    path('discussion/edit/<int:id>/', edit_discussion, name='edit_discussion'),
    path('forums/json-for/', show_json_forum, name = 'jsonForum'),
    path('forums/json-dis/', show_json_discussion, name = 'jsonDisc'),
    path('forum/add-discussion/', add_discussion_json, name='add_discussion_json'),
    path('forum/add/', add_forum_json, name='add_forum_json'),
    path('get-username/', get_username, name='get_username'),
    path('get-user-info/', get_user_info, name='get_user_info'),
    path('discussion/<int:pk>/delete/', delete_discussion_json, name='delete_discussion_json'),
    path('forum/<int:pk>/delete/', delete_forum_json, name='delete_forum_json'), #flutter delete discuss
    path('forum/<int:pk>/edit/', edit_forum_json, name='edit_forum_json'),
    path('discussion/<int:pk>/edit/', edit_discussion_json, name='edit_discussion_json'), #flutter edit stuff
]