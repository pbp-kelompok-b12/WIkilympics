# athletes/urls.py
from django.urls import path
from athletes.views import (
    show_main, create_athlete, show_athlete, show_json, show_json_by_id, 
    edit_athlete, delete_athlete, create_athlete_entry_ajax, 
    edit_athlete_entry_ajax, delete_athlete_entry_ajax,
    flutter_get_athletes, flutter_create_athlete, flutter_edit_athlete,
    flutter_delete_athlete, flutter_get_athlete_detail
)

app_name = 'athletes'

urlpatterns = [
    path('', show_main, name='show_main'),  
    path('create-athlete/', create_athlete, name='create_athlete'),
    path('create-athlete-ajax/', create_athlete_entry_ajax, name='create_athlete_entry_ajax'),
    path('json/', show_json, name='show_json'),
    path('json/<str:athlete_id>/', show_json_by_id, name='show_json_by_id'),
    path('edit-athlete-ajax/<uuid:id>/', edit_athlete_entry_ajax, name='edit_athlete_entry_ajax'),
    path('delete-athlete-ajax/<uuid:id>/', delete_athlete_entry_ajax, name='delete_athlete_entry_ajax'),
    path('<uuid:id>/', show_athlete, name='show_athlete'),
    path('<uuid:id>/edit', edit_athlete, name='edit_athlete'),
    path('<uuid:id>/delete', delete_athlete, name='delete_athlete'),
    
    # Endpoints khusus untuk Flutter
    path('flutter/', flutter_get_athletes, name='flutter_get_athletes'),
    path('flutter/create/', flutter_create_athlete, name='flutter_create_athlete'),
    path('flutter/<uuid:id>/edit/', flutter_edit_athlete, name='flutter_edit_athlete'),
    path('flutter/<uuid:id>/delete/', flutter_delete_athlete, name='flutter_delete_athlete'),
    path('flutter/<uuid:id>/', flutter_get_athlete_detail, name='flutter_get_athlete_detail'),
]