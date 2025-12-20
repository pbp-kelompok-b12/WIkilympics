from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from sports.models import Sports
from article.models import Article
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from article.forms import ArticleForm

import requests

from django.utils.html import strip_tags
import json
import re

# Create your views here.
def show_articles(request):
    return render(request, 'show_articles.html')

def normalize_string(text):
    text = text.lower().replace('_', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def show_json(request):
    article_list = Article.objects.all().order_by('-created')
    all_sports = Sports.objects.all()

    data = []
    for article in article_list:
        clean_article_category = normalize_string(article.category)

        sport_id = None
        sport_obj = Sports.objects.filter(sport_name__iexact=clean_article_category).first()
        
        if sport_obj is not None:
            sport_id = str(sport_obj.pk)
        else:
            sport_id=None
        # sport_id = str(sport_obj.pk)

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
            'sport_id': sport_id,
            'created': article.created.isoformat(),
            'thumbnail': article.thumbnail,
            'likes': article.like_user.count(),
          
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
        'likes': article.like_user.count(),
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
@csrf_exempt
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
@csrf_exempt
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
    return JsonResponse({'success': True, 'likes': article.like_user.count()})

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def create_article_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        title = strip_tags(data.get("title", ""))
        content = strip_tags(data.get("content", ""))  
        category = data.get("category", "")
        thumbnail = data.get("thumbnail", "")
        
        new_article = Article(
            title=title, 
            content=content,
            category=category,
            thumbnail=thumbnail,
        )
        new_article.save()
        
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)  

@csrf_exempt
def edit_article_flutter(request, id):
    if request.method == 'POST':
        article = Article.objects.get(pk=id)
        
        data = json.loads(request.body)

        article.title = strip_tags(data.get("title", article.title))
        article.content = strip_tags(data.get("content", article.content))
        article.category = data.get("category", article.category)
        article.thumbnail = data.get("thumbnail", article.thumbnail)

        article.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status:error"}, status=401)

@csrf_exempt
def delete_article_flutter(request, id):
    if request.method == 'POST':
        article = Article.objects.get(pk=id)
        article.delete()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=400)