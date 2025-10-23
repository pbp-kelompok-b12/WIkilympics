from django.urls import path
from sports.views import show_main, create_sport, show_sport, show_json, show_json_by_id, edit_sport, delete_sport

app_name = 'sports'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-sport/', create_sport, name='create_sport'),
    path('sports/<str:id>/', show_sport, name='show_sport'),
    path('json/', show_json, name='show_json'),
    path('json/<str:sports_id>/', show_json_by_id, name='show_json_by_id'),
    path('sports/<uuid:id>/edit', edit_sport, name='edit_sport'),
    path('sports/<uuid:id>/delete', delete_sport, name='delete_sport'),
]
