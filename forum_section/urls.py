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
]