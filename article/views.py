from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from article.models import Article

# Create your views here.
def article_list(request):
    articles_list = Article.objects.all()
    context = {'articles' : article_list}
    return render(request, 'article_list.html', context)

def show_json(request):
    article_list = Article.objects.all()
    data = [
        {
            'id' : str(article.id),
            'title' : article.title,
            'content' : article.content,
            'category': article.category,
            'created': article.created.isoformat(),
            'thumbnail': article.thumbnail,
            'likes': article.like_count,
        }
        for article in article_list
    ]
    return JsonResponse(data, safe=False)   #data dalam list

def show_json_id(request, article_id) :
    article = get_object_or_404(Article, pk=article_id)
    data = {
        'id' : str(article.id),
        'title' : article.title,
        'content' : article.content,
        'category': article.category,
        'created': article.created.isoformat(),
        'thumbnail': article.thumbnail,
        'likes': article.like_count,
    }
    return JsonResponse(data)

@login_required(login_url='main:login_user')
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

@login_required(login_url='main:login_user')
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
