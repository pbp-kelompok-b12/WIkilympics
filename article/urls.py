from django.urls import path
from article.views import show_articles, show_json, show_json_id, add_article, edit_article, delete_article, like_article, dislike_article, article_detail

app_name = 'article'

urlpatterns = [
    path('', show_articles, name='show_articles'),
    path('json/', show_json, name='show_json'),
    path('json/<uuid:article_id>/', show_json_id, name='show_json_id'),
    
    path('add/', add_article, name='add_article'),
    path('edit/<uuid:id>/', edit_article, name='edit_article'),
    path('delete/<uuid:id>/', delete_article, name='delete_article'),

    path('detail/<uuid:id>/', article_detail, name='article_detail'),

    path('like/<uuid:article_id>/', like_article, name='like_article'),
    path('dislike/<uuid:article_id>/', dislike_article, name='dislike_article'),

]