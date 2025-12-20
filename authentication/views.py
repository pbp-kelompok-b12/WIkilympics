<<<<<<< HEAD
# authentication/views.py
=======
>>>>>>> feat/dev
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
import json
from django.contrib.auth.decorators import login_required

<<<<<<< HEAD
=======
# Create your views here.

>>>>>>> feat/dev
@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
<<<<<<< HEAD
            return JsonResponse({
                "username": user.username,
                "status": True,
=======
            # Login status successful.
            return JsonResponse({
                "username": user.username,
                "status": True,
                "is_superuser": user.is_superuser,
>>>>>>> feat/dev
                "message": "Login successful!"
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)
<<<<<<< HEAD
=======

>>>>>>> feat/dev
    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed, please check your username or password."
        }, status=401)
        
<<<<<<< HEAD
=======
        
>>>>>>> feat/dev
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

<<<<<<< HEAD
=======
        # Check if the passwords match
>>>>>>> feat/dev
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
<<<<<<< HEAD
=======
        # Check if the username is already taken
>>>>>>> feat/dev
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
<<<<<<< HEAD
=======
        # Create the new user
>>>>>>> feat/dev
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
<<<<<<< HEAD
=======
    
>>>>>>> feat/dev
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
<<<<<<< HEAD
=======
@login_required
>>>>>>> feat/dev
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)

<<<<<<< HEAD
@csrf_exempt
=======
>>>>>>> feat/dev
@login_required
def get_user_status(request):
    return JsonResponse({
        'is_superuser': request.user.is_superuser,
<<<<<<< HEAD
        'is_staff': request.user.is_staff,
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
    })
=======
        'username': request.user.username,
    }) 

from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

@csrf_exempt
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        new_password = request.POST.get('password')

        if new_password:
            if check_password(new_password, user.password):
                return JsonResponse({
                    "status": "error", 
                    "message": "New password cannot be the same as the old one!"
                }, status=400)
            
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user) 
            
            return JsonResponse({
                "status": "success", 
                "message": "Password updated! You are still logged in."
            })
        
        return JsonResponse({"status": "error", "message": "Password cannot be empty"}, status=400)

@csrf_exempt
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return JsonResponse({"status": "success", "message": "Account deleted successfully."})
>>>>>>> feat/dev
