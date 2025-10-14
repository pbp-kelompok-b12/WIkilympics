from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from article.models import Article

# Create your views here.
def article_list(request):
    articles_list = Article.objects.all()
    context = {'articles' : article_list}
    return render(request, 'article_list.html', context)

# @login_required
def like_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.user in article.like_user.all():
        article.like_user.remove(request.user)
    elif request.user in article.dislike_user.all():
        article.dislike_user.remove(request.user)
        article.like_user.add(request.user)
    else:
        article.like_user.add(request.user)

    return JsonResponse({'success': True, 'likes': article.like_count})

# @login_required
def dislike_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.user in article.dislike_user.all():
        article.dislike_user.remove(request.user)
    elif request.user in article.like_user.all():
        article.like_user.remove(request.user)
        article.dislike_user.add(request.user)
    else:
        article.dislike_user.add(request.user)

    return JsonResponse({'success': True})