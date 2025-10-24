from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from sports.models import Sports
from article.models import Article
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from article.forms import ArticleForm

# Create your views here.
def show_articles(request):
    return render(request, 'show_articles.html')

def show_json(request):
    article_list = Article.objects.all().order_by('-created')
    data = []
    for article in article_list:
        is_liked = False
        is_disliked = False
        if request.user.is_authenticated:
            is_liked = article.like_user.filter(id=request.user.id).exists()
            is_disliked = article.dislike_user.filter(id=request.user.id).exists()

        data.append({
            'id': str(article.id),
            'title': article.title,
            'content': article.content,
            'category': article.category,
            'created': article.created.isoformat(),
            'thumbnail': article.thumbnail,
            'likes': article.like_count,
          
            'is_liked': is_liked,
            'is_disliked': is_disliked,
        })
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

@csrf_exempt
@require_POST
def add_article(request):
    form = ArticleForm(request.POST) 

    if form.is_valid():
        new_article = form.save(commit=False)
        new_article.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@require_POST
def edit_article(request, id):
    article = get_object_or_404(Article, pk=id)
   
    form = ArticleForm(request.POST, instance=article) 

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'Article updated successfully.'}, status=200)
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    

@require_POST
def delete_article(request, id):
    article = get_object_or_404(Article, pk=id)
    article.delete()
    return JsonResponse({'success':True})

def article_detail(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('article:show_articles'))
    
    article = get_object_or_404(Article, pk=id)

    clean_category_name = article.category.replace('_', ' ').title()

    sport_id=None
    try:
        sport_obj = Sports.objects.get(sport_name__iexact=article.category)
        sport_id = str(sport_obj.id)
    except Sports.DoesNotExist:
        pass
    
    context={'article':article, 'sport_id':sport_id, 'clean_category_name': clean_category_name}
    return render(request, "article_detail.html", context)

# @login_required(login_url='main:login_user')
def like_article(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse ({'success': False}, status=403)
    
    article = get_object_or_404(Article, pk=article_id)

    if request.user in article.like_user.all():
        article.like_user.remove(request.user)
    elif request.user in article.dislike_user.all():
        article.dislike_user.remove(request.user)
        article.like_user.add(request.user)
    else:
        article.like_user.add(request.user)
    return JsonResponse({'success': True, 'likes': article.like_user.count()})

# @login_required(login_url='main:login_user')
def dislike_article(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse ({'success': False}, status=403)
    
    article = get_object_or_404(Article, pk=article_id)

    if request.user in article.dislike_user.all():
        article.dislike_user.remove(request.user)
    elif request.user in article.like_user.all():
        article.like_user.remove(request.user)
        article.dislike_user.add(request.user)
    else:
        article.dislike_user.add(request.user)
    return JsonResponse({'success': True})
