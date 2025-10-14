from django.urls import path
from article.views import article_list, like_article, dislike_article

app_name = 'article'

urlpatterns = [
    path('', article_list, name='article_list'),
    path('like/<uuid:article_id>/', like_article, name='like_article'),
    path('dislike/<uuid:article_id>/', dislike_article, name='dislike_article'),
]