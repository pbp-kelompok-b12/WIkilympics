from django.urls import path
<<<<<<< HEAD
from authentication.views import login, register, logout, get_user_status
=======
from authentication.views import login, register, logout, get_user_status, edit_profile, delete_account
>>>>>>> feat/dev

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('status/', get_user_status, name="get_user_status"),
<<<<<<< HEAD
=======
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('delete-account/', delete_account, name='delete_account'),
>>>>>>> feat/dev
]