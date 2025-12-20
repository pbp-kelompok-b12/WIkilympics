from django.urls import path
from sports.views import show_main, create_sport, show_sport, show_json, show_json_by_id, edit_sport, delete_sport, create_sport_entry_ajax, edit_sport_entry_ajax, delete_sport_entry_ajax, proxy_image, create_sport_flutter, edit_sport_flutter, delete_sport_flutter

app_name = 'sports'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-sport/', create_sport, name='create_sport'),
    path('sports/<str:id>/', show_sport, name='show_sport'),
    path('json/', show_json, name='show_json'),
    path('json/<str:sports_id>/', show_json_by_id, name='show_json_by_id'),
    path('sports/<uuid:id>/edit', edit_sport, name='edit_sport'),
    path('sports/<uuid:id>/delete', delete_sport, name='delete_sport'),
    path('create-sport-ajax/', create_sport_entry_ajax, name='create_sport_entry_ajax'),
    path('edit-sport-ajax/<uuid:id>/', edit_sport_entry_ajax, name='edit_sport_entry_ajax'),
    path('delete-sport-ajax/<uuid:id>/', delete_sport_entry_ajax, name='delete_sport_entry_ajax'),
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('create-flutter/', create_sport_flutter, name='create_sport_flutter'),
    path('edit-flutter/<uuid:id>/', edit_sport_flutter, name='edit_sport_flutter'),
    path('delete-flutter/<uuid:id>/', delete_sport_flutter, name='delete_sport_flutter'),
]